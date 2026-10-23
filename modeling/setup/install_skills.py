#!/usr/bin/env python3
"""Install / package the modeling skills for Claude Code, Codex, ChatGPT and the Claude app.

Python 3.10+, standard library only. Run without arguments for an interactive menu.

  python install_skills.py claude-code                 # ~/.claude/skills/<skill>
  python install_skills.py claude-code --project DIR   # DIR/.claude/skills/<skill>
  python install_skills.py codex                       # ~/.agents/skills/<skill>  (+ --codex-legacy: ~/.codex/skills)
  python install_skills.py chatgpt-desktop             # same local skills folder Codex uses (~/.agents/skills)
  python install_skills.py claude-app                  # dist/claude-app/<skill>.zip  -> upload in Customize > Skills
  python install_skills.py chatgpt-web                 # dist/chatgpt/<skill>.zip     -> upload in ChatGPT Skills
  python install_skills.py blender                     # bl_*.py into Blender's user scripts/modules
  python install_skills.py mcp                         # print Blender-MCP setup for every client
  python install_skills.py check                       # validate all skills (frontmatter, links)
  python install_skills.py smoke                       # run the Blender smoke tests (needs Blender)
  python install_skills.py all                         # claude-code + codex + blender + both zip sets

Common options: --skills a,b  --dest DIR  --dry-run  --no-backup  --uninstall  --blender PATH
Installed copies are SELF-CONTAINED: skills that use the shared Blender library get their own copy
of model-prompt-to-blender/scripts, references and assets, so each one also works on its own.
Existing installs are moved to ~/.skill_backups/<target>/ before being replaced.
"""
import argparse, os, re, shutil, subprocess, sys, tempfile, time, zipfile, glob, platform
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent                                  # share_skill/modeling
SKILLS = ['reference-to-concept', 'concept-to-model-prompt', 'model-prompt-to-blender',
          'blender-detail-repair', 'blender-model-verify']
PROVIDER = 'model-prompt-to-blender'
DEPENDENTS = {'blender-detail-repair', 'blender-model-verify'}
VENDOR_DIRS = ('scripts', 'references', 'assets')
BLENDER_MODULES = ('bl_build.py', 'bl_detail.py', 'bl_materials.py', 'bl_views.py', 'bl_check.py',
                   'bl_symmetry.py', 'bl_images.py')
IGNORE = shutil.ignore_patterns('__pycache__', '*.pyc', '_smoke_out', '*.blend1', '.DS_Store')
HOME = Path.home()


def log(*a):
    print(*a, flush=True)


# ----------------------------------------------------------------------------- validation
FM = re.compile(r'^---\s*\nname:\s*(.+?)\s*\ndescription:\s*(.+?)\s*\n(?:[a-z_-]+:.*\n)*---\s*\n', re.S)


def validate(skill_dir: Path):
    errs = []
    md = skill_dir / 'SKILL.md'
    if not md.exists():
        return ['missing SKILL.md']
    text = md.read_text(encoding='utf-8')
    m = FM.match(text)
    if not m:
        return ['frontmatter must start with name: and description:']
    name, desc = m.group(1).strip(), m.group(2).strip()
    if not re.fullmatch(r'[a-z0-9-]{1,64}', name):
        errs.append('name must be lowercase letters/digits/hyphens, <= 64 chars: %r' % name)
    if name != skill_dir.name:
        errs.append('name %r must match folder %r' % (name, skill_dir.name))
    if not desc or len(desc) > 1024:
        errs.append('description must be 1..1024 chars (has %d)' % len(desc))
    if text.count('\n') >= 500:
        errs.append('SKILL.md should stay under 500 lines')
    for link in re.findall(r'\]\(([^)#]+)\)', text):
        if re.match(r'[a-z]+://', link):
            continue
        if not (skill_dir / link).resolve().exists():
            errs.append('broken link: %s' % link)
    return errs


# ----------------------------------------------------------------------------- staging
def stage(skills, tmp: Path):
    """Copy skills into tmp; make dependents self-contained."""
    out = {}
    for s in skills:
        src = SRC / s
        if not src.is_dir():
            raise SystemExit('skill not found: %s' % src)
        dst = tmp / s
        shutil.copytree(src, dst, ignore=IGNORE)
        if s in DEPENDENTS:
            prov = SRC / PROVIDER
            for d in VENDOR_DIRS:
                if (prov / d).is_dir():
                    shutil.copytree(prov / d, dst / d, ignore=IGNORE, dirs_exist_ok=True)
            md = dst / 'SKILL.md'
            t = md.read_text(encoding='utf-8')
            t = t.replace('../%s/' % PROVIDER, '')
            t = t.replace('Uses the scripts and references of the sibling skill `%s`; install both side by side.' % PROVIDER,
                          'Shared files from `%s` are bundled in this folder.' % PROVIDER)
            t = t.replace('Uses `scripts/`; install both side by side.', 'Shared files from `%s` are bundled in this folder.' % PROVIDER)
            md.write_text(t, encoding='utf-8')
            (dst / 'VENDORED.txt').write_text('scripts/, references/, assets/ copied from %s at %s\n'
                                              % (PROVIDER, time.strftime('%Y-%m-%d %H:%M')), encoding='utf-8')
        errs = validate(dst)
        if errs:
            raise SystemExit('validation failed for %s:\n  ' % s + '\n  '.join(errs))
        out[s] = dst
    return out


# ----------------------------------------------------------------------------- targets
def install_dirs(staged, dest: Path, target, args):
    dest.mkdir(parents=True, exist_ok=True)
    for s, src in staged.items():
        d = dest / s
        if args.dry_run:
            log('[dry-run] %s -> %s' % (s, d))
            continue
        if d.exists():
            if not args.no_backup:
                b = HOME / '.skill_backups' / target / ('%s-%s' % (s, time.strftime('%Y%m%d-%H%M%S')))
                b.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(d), str(b))
                log('  backup: %s' % b)
            else:
                shutil.rmtree(d)
        if args.uninstall:
            log('  removed %s' % d)
            continue
        shutil.copytree(src, d)
        log('  installed %s -> %s' % (s, d))


def zip_skills(staged, out_dir: Path, args):
    out_dir.mkdir(parents=True, exist_ok=True)
    for s, src in staged.items():
        z = out_dir / (s + '.zip')
        if args.dry_run:
            log('[dry-run] zip %s' % z)
            continue
        with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
            for p in sorted(src.rglob('*')):
                if p.is_file():
                    zf.write(p, Path(s) / p.relative_to(src))       # folder at the top of the zip
        names = zipfile.ZipFile(z).namelist()
        assert all(n.startswith(s + '/') for n in names) and (s + '/SKILL.md') in names, z
        log('  %s (%d files)' % (z, len(names)))


def blender_module_dirs(args):
    if args.blender_modules:
        return [Path(args.blender_modules)]
    sysname = platform.system()
    if sysname == 'Windows':
        base = Path(os.environ.get('APPDATA', HOME / 'AppData/Roaming')) / 'Blender Foundation' / 'Blender'
    elif sysname == 'Darwin':
        base = HOME / 'Library/Application Support/Blender'
    else:
        base = HOME / '.config/blender'
    vers = [args.blender_version] if args.blender_version else sorted(
        p.name for p in base.glob('*') if p.is_dir() and re.fullmatch(r'\d+\.\d+', p.name))
    if not vers:
        raise SystemExit('No Blender user folder found under %s. Start Blender once or pass --blender-version X.Y' % base)
    return [base / v / 'scripts' / 'modules' for v in vers]


def install_blender_modules(args):
    srcdir = SRC / PROVIDER / 'scripts'
    for d in blender_module_dirs(args):
        if args.dry_run:
            log('[dry-run] modules -> %s' % d)
            continue
        d.mkdir(parents=True, exist_ok=True)
        for m in BLENDER_MODULES:
            t = d / m
            if args.uninstall:
                if t.exists():
                    t.unlink()
                continue
            shutil.copy2(srcdir / m, t)
        log('  %s %s' % ('removed modules from' if args.uninstall else 'modules ->', d))
    if not args.uninstall:
        log('  Inside Blender:  import bl_build as bl, bl_detail as dl  (no sys.path needed)')


def find_blender(args):
    if args.blender:
        return args.blender
    cands = []
    if platform.system() == 'Windows':
        cands = sorted(glob.glob(r'C:\Program Files\Blender Foundation\Blender *\blender.exe'), reverse=True)
    elif platform.system() == 'Darwin':
        cands = ['/Applications/Blender.app/Contents/MacOS/Blender']
    w = shutil.which('blender')
    if w:
        cands.insert(0, w)
    for c in cands:
        if os.path.exists(c):
            return c
    raise SystemExit('Blender executable not found; pass --blender PATH')


def smoke(args):
    exe = find_blender(args)
    tests = SRC / PROVIDER / 'scripts' / 'tests'
    out = Path(tempfile.mkdtemp(prefix='oow_smoke_'))
    ok = True
    for t, needle in (('smoke_test.py', 'SMOKE_OK'), ('no_shell_test.py', 'NO_SHELL_OK')):
        log('  running %s with %s ...' % (t, exe))
        p = subprocess.run([exe, '-b', '--factory-startup', '--python', str(tests / t), '--', str(out)],
                           capture_output=True, text=True, errors='replace')
        lines = [l for l in p.stdout.splitlines() if needle in l or 'device' in l.lower() or 'Error' in l]
        log('   ' + '\n   '.join(lines[-4:]))
        ok &= any(needle in l for l in lines)
    log('  smoke tests: %s  (outputs in %s)' % ('PASS' if ok else 'FAIL', out))
    return ok


MCP_HELP = r"""
Blender side (once per machine)
  1. Install uv (https://docs.astral.sh/uv/) so `uvx` is available.
  2. Install/refresh the Blender add-on:   uvx mcp-for-blender install-addon
  3. In Blender: Preferences > Add-ons > enable "Interface: Blender MCP", then Start MCP Server
     (N-panel). Keep Blender open while the agent works.

Client side (pick yours)
  Claude Code (all projects):  claude mcp add --scope user blender -- uvx mcp-for-blender
  Claude desktop app:          claude_desktop_config.json ->
      {"mcpServers": {"blender": {"command": "uvx", "args": ["mcp-for-blender"]}}}
  Codex CLI / ChatGPT desktop (Codex):  ~/.codex/config.toml ->
      [mcp_servers.blender]
      command = "uvx"
      args = ["mcp-for-blender"]
  ChatGPT web / claude.ai web: cannot reach a local stdio MCP server; use a desktop/CLI client for
      the Blender stages (skills 3-5). Skills 1-2 (concept + prompt) work anywhere.
"""


def menu():
    opts = ['claude-code', 'codex', 'chatgpt-desktop', 'claude-app', 'chatgpt-web', 'blender', 'mcp', 'check', 'smoke', 'all']
    log('Modeling skills installer\n')
    for i, o in enumerate(opts, 1):
        log('  %d) %s' % (i, o))
    sel = input('\nChoose (e.g. 1,6): ').strip()
    return [opts[int(x) - 1] for x in re.split(r'[,\s]+', sel) if x.isdigit() and 0 < int(x) <= len(opts)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('targets', nargs='*')
    ap.add_argument('--skills', help='comma list (default: all five)')
    ap.add_argument('--project', help='claude-code: install into PROJECT/.claude/skills')
    ap.add_argument('--dest', help='override destination folder (installs / zips)')
    ap.add_argument('--codex-legacy', action='store_true', help='codex: also install into ~/.codex/skills')
    ap.add_argument('--blender', help='Blender executable for smoke')
    ap.add_argument('--blender-version', help='blender: target X.Y user folder')
    ap.add_argument('--blender-modules', help='blender: explicit modules folder')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--no-backup', action='store_true')
    ap.add_argument('--uninstall', action='store_true')
    args = ap.parse_args()
    targets = args.targets or menu()
    if 'all' in targets:
        targets = ['claude-code', 'codex', 'blender', 'claude-app', 'chatgpt-web']
    skills = [s.strip() for s in args.skills.split(',')] if args.skills else SKILLS
    rc = 0
    with tempfile.TemporaryDirectory() as td:
        staged = None
        for t in targets:
            log('\n== %s' % t)
            if t in ('claude-code', 'codex', 'chatgpt-desktop', 'claude-app', 'chatgpt-web', 'check') and staged is None:
                staged = stage(skills, Path(td))
            if t == 'check':
                for s in skills:
                    errs = validate(SRC / s)
                    where = [n for n, d in (('claude-code', HOME / '.claude' / 'skills'), ('agents', HOME / '.agents' / 'skills'),
                                            ('codex-legacy', HOME / '.codex' / 'skills')) if (d / s / 'SKILL.md').is_file()]
                    log('  %-26s source %s | packaged copy OK | installed: %s'
                        % (s, 'OK' if not errs else 'FAIL: ' + '; '.join(errs), ', '.join(where) or '-'))
                    rc |= bool(errs)
            elif t == 'claude-code':
                dest = Path(args.dest) if args.dest else (Path(args.project) / '.claude' / 'skills' if args.project else HOME / '.claude' / 'skills')
                install_dirs(staged, dest, 'claude-code', args)
                log('  Use: type /<skill-name> or describe the task; restart Claude Code if it was running.')
            elif t in ('codex', 'chatgpt-desktop'):
                dests = [Path(args.dest)] if args.dest else [HOME / '.agents' / 'skills']
                if args.codex_legacy and not args.dest:
                    dests.append(HOME / '.codex' / 'skills')
                for d in dests:
                    install_dirs(staged, d, t, args)
                log('  Use: $<skill-name> (Codex CLI / IDE) or the Skills sidebar / @skill in the ChatGPT desktop app; restart the app.')
            elif t == 'claude-app':
                zip_skills(staged, Path(args.dest) if args.dest else HERE / 'dist' / 'claude-app', args)
                log('  Upload each zip at claude.ai > Customize > Skills (code execution must be on), then turn it on.')
            elif t == 'chatgpt-web':
                zip_skills(staged, Path(args.dest) if args.dest else HERE / 'dist' / 'chatgpt', args)
                log('  Upload each zip in ChatGPT > Skills (plan/admin must allow custom skills).')
            elif t == 'blender':
                install_blender_modules(args)
            elif t == 'mcp':
                log(MCP_HELP)
            elif t == 'smoke':
                rc |= not smoke(args)
            else:
                log('  unknown target: %s' % t)
                rc = 2
    sys.exit(rc)


if __name__ == '__main__':
    main()
