STUDS.SG website

The fundraising site for STUDS, a group of Singapore men racing for charity. Two static pages, no build step.
AI assistants: read AGENTS.md first. It has the full guide and the owner's rules.

WHAT'S HERE
  public/               Everything the site serves. Publish this folder.
    index.html          The fundraising page: HTML, CSS and JavaScript in one file.
    about.html          The About page.
    images/             Photos, logos (sponsor logos in images/sponsors/) and studs-share.jpg,
                        the preview WhatsApp and social apps show when the link is shared.
    _headers            Security and caching headers, read by Netlify.
    llms.txt            Plain facts about STUDS for AI assistants.
  netlify.toml          Netlify settings: no build step, publish the public folder as written.
  tools/update_csp.py   Run after editing either script in index.html (see SECURITY).
  tools/check_layout.py Loads both pages at phone and desktop sizes and reports anything broken.
  tools/photo.py        Prepares a new photo for the photo walls.
  AGENTS.md, CLAUDE.md  The guide for AI assistants (and anyone editing in depth).

PUBLISH
  Netlify project "studs-sg". Publish directory: public. No build command.
  If the site is in a GitHub repository linked to Netlify, pushing to the main branch publishes it.
  Otherwise drag the public folder onto the project's Deploys page in Netlify.
  The address is https://studs.sg (www.studs.sg and studs-sg.netlify.app reach the same site).

EVERYDAY EDITS
  Season 2 total   In public/index.html find the comment SEASON 2 TOTAL. Change the figure and the
                   date. Change llms.txt to match.
  Copy             Plain text inside each <section> of index.html and about.html.
  Photos           Real photos only, never AI images. Nobody may be cropped out: each photo's frame
                   has the same shape as the file. tools/photo.py prepares a new photo in all four
                   sizes and formats and prints the markup; the steps are in AGENTS.md.
  Fundraiser link  Find and replace the GoFundMe address in index.html (links, the share box, the
                   studs-config block and the structured data), about.html and llms.txt.
  Sponsors         Footer of both pages; logos in public/images/sponsors/.

SECURITY
  The page loads nothing from other sites: no trackers, ads, cookies or third-party scripts.
  public/_headers holds a strict Content Security Policy that allows only the page's two inline
  scripts, by hash. After editing either script, run:  python3 tools/update_csp.py
  Without that, browsers block the script and the page stops moving and loses its Share button.
  The WhatsApp number behind the About page's sponsorship button is public; anyone can see it.

CHECKING
  python3 tools/check_layout.py   (needs: pip install playwright; python3 -m playwright install)
  It must end with "All clear". Then look at both pages on a phone.
