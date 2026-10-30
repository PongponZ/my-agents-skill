#!/usr/bin/env python3
"""Install / package the modeling skills for Claude Code, Codex, ChatGPT and the Claude app.

Python 3.10+, standard library only. Run without arguments for an interactive menu.

  python install_skills.py claude-code                 # ~/.claude/skills/<skill>
  python install_skills.py claude-code --project DIR   # DIR/.claude/skills/<skill>
  python install_skills.py codex                       # ~/.agents/skills/<skill>  (+ --codex-legacy: ~/.codex/skills)
  python install_skills.py chatgpt-desktop             # same local skills folder Codex uses (~/.agents/skills)
  python install_skills.py claude-app                  # dist/claude-app/<skill>.zip  -> upload in Customize > Skills
  python install_skills.py chatgpt-web                 # dist/chatgpt/<skill>.zip     -> upload in ChatGPT Skills
  python install_skills.py check                       # validate all skills (frontmatter, links)
  python install_skills.py all                         # claude-code + codex + both zip sets

Common options: --skills a,b  --dest DIR  --dry-run  --no-backup  --uninstall
Existing installs are moved to ~/.skill_backups/<target>/ before being replaced.
"""
import argparse, re, shutil, sys, tempfile, time, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent                                  # share_skill/modeling
SKILLS = ['reference-to-prompt', 'reference-to-concept', 'concept-to-model-prompt']
BUNDLED_STAGES = {'reference-to-prompt': ('reference-to-concept', 'concept-to-model-prompt')}
IGNORE = shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store')
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
    """Copy skills and bundle the main workflow's stages for standalone use."""
    out = {}
    for s in skills:
        src = SRC / s
        if not src.is_dir():
            raise SystemExit('skill not found: %s' % src)
        dst = tmp / s
        shutil.copytree(src, dst, ignore=IGNORE)
        for dependency in BUNDLED_STAGES.get(s, ()):
            bundled = dst / 'workflows' / dependency
            shutil.copytree(SRC / dependency, bundled, ignore=IGNORE)
            errors = validate(bundled)
            if errors:
                raise SystemExit('validation failed for bundled %s:\n  ' % dependency + '\n  '.join(errors))
            main_md = dst / 'SKILL.md'
            content = main_md.read_text(encoding='utf-8')
            content = content.replace('../%s/' % dependency, 'workflows/%s/' % dependency)
            main_md.write_text(content, encoding='utf-8')
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


def menu():
    opts = ['claude-code', 'codex', 'chatgpt-desktop', 'claude-app', 'chatgpt-web', 'check', 'all']
    log('Modeling skills installer\n')
    for i, o in enumerate(opts, 1):
        log('  %d) %s' % (i, o))
    sel = input('\nChoose (e.g. 1,2): ').strip()
    return [opts[int(x) - 1] for x in re.split(r'[,\s]+', sel) if x.isdigit() and 0 < int(x) <= len(opts)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('targets', nargs='*')
    ap.add_argument('--skills', help='comma list (default: main workflow and both stage skills)')
    ap.add_argument('--project', help='claude-code: install into PROJECT/.claude/skills')
    ap.add_argument('--dest', help='override destination folder (installs / zips)')
    ap.add_argument('--codex-legacy', action='store_true', help='codex: also install into ~/.codex/skills')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--no-backup', action='store_true')
    ap.add_argument('--uninstall', action='store_true')
    args = ap.parse_args()
    targets = args.targets or menu()
    if 'all' in targets:
        targets = ['claude-code', 'codex', 'claude-app', 'chatgpt-web']
    skills = [s.strip() for s in args.skills.split(',')] if args.skills else SKILLS
    unknown_skills = set(skills) - set(SKILLS)
    if unknown_skills:
        ap.error('unknown skills: ' + ', '.join(sorted(unknown_skills)))
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
            else:
                log('  unknown target: %s' % t)
                rc = 2
    sys.exit(rc)


if __name__ == '__main__':
    main()
