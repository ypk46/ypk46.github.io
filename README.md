# Personal Website

Source for [ykimura.dev](https://ykimura.dev), served by GitHub Pages from `main`. Plain HTML and one
stylesheet, no build step.

- `index.html` (About), `projects/`, `experience/`, `writing/`: the four pages. They share the navbar and
  footer markup, so change those in all four.
- `style.css`: design tokens on `:root` (dark values under `prefers-color-scheme: dark`) and every page's
  styles. Mobile rules live in the `max-width: 900px` block at the end.
- `projects/projects.js`: the project filters. Each card's `data-category` matches a filter chip; without
  JavaScript the chips stay hidden and every card shows.
- `app-ads.txt`: AdMob publisher line. It must stay at the domain root.
- `games/privacy/`: privacy policy shared by every game; add each new game to its "Games covered" list.
- `cv.pdf`: the CV linked from Home and Experience; replace the file to update it.
- Writing: `.github/workflows/medium.yml` runs `scripts/medium.py` daily. It merges the Medium feed into
  `data/posts.json` and rewrites the generated blocks: the latest posts on Home (`medium` markers in
  `index.html`) and the latest post card and year archive on Writing (`medium-latest` and `medium-archive`
  markers in `writing/index.html`). The feed only carries the 10 newest posts, so `posts.json` is the
  archive: never prune it, and add older posts to it by hand. Run it locally with
  `python3 scripts/medium.py yuyik46`.
