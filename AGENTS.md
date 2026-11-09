# STUDS.SG: guide for AI assistants

Read this before changing anything. It explains how the site is built, the owner's rules, and how to check and publish a change. People can use it too; README.txt is the short version.

## The site in one paragraph

STUDS (Support Through United Dad Strength) is a group of Singapore men who race triathlons and other endurance events to raise money for charity. This is their fundraising site: two static pages, `public/index.html` (the Season 2 fundraiser) and `public/about.html`. There is no framework and no build step. Each page holds its own HTML, CSS and JavaScript. It is hosted on Netlify.

## The owner's rules (follow these every time)

- Writing: British English. No em dashes. No filler, hype or tell-tale AI phrasing. Short, plain sentences that sound like a person wrote them.
- Call the group "men", not "dads": not every member is a father. The name itself stays "Support Through United Dad Strength".
- Never describe STUDS as a charity or a foundation: registration is in progress. Donations go to Friends Without A Border through GoFundMe.
- Never name a donor or say who gave what unless the owner confirms it.
- Every Donate and Share link uses exactly https://www.gofundme.com/f/studs-season-2-bigger-bolder-and-back-for-more
- Photos: real photos only. Never use AI-generated or AI-edited images (one was removed for being AI). People must be whole and central: never crop anyone out of a photo. Show children only in group shots the owner has chosen (the Phuket family finish photo).
- Try not to show the same person prominently in more than one photo. Group shots are fine.
- Design: navy `#0C1A33`, off-white `#F3F5F6` and green `#7DC242` as the accent, with mist `#A9B4C6` and slate `#4A5568` for quieter text. One typeface, Archivo, self-hosted. Strict grid, very large headlines, plenty of space. No drop shadows or frames on photos, no gradients, no stock images.
- Sponsors in the footer: only Boomarang Bistro & Bar and Tsunami, as white logos. Don't add or remove sponsors without the owner.
- Ask before adding anything that shows the owner's WhatsApp number. The "Join us" buttons were removed to keep it from being spammed. Only the About page's sponsorship button uses it now.
- Ask the owner before publishing. The live site is shared publicly.

## Files

```
AGENTS.md              this guide (CLAUDE.md points here)
README.txt             the short guide for people
netlify.toml           Netlify settings: publish the public folder exactly as written
tools/update_csp.py    refreshes the script hashes in public/_headers; run it after editing any script
tools/check_layout.py  loads both pages at phone and desktop sizes and reports layout problems
public/                everything the site serves
  index.html           the fundraising page: HTML, CSS and both scripts inline
  about.html           the About page: HTML and CSS, no JavaScript
  _headers             security and caching headers, including the Content Security Policy
  images/              photos, the STUDS.SG logo files, sponsor logos (images/sponsors/), studs-share.jpg (link preview)
  fonts/               the Archivo variable font (woff2)
  llms.txt             plain facts for AI assistants; keep it in step with the pages
  robots.txt, sitemap.xml, site.webmanifest, favicon.*, icon-*.png, apple-touch-icon.png
```

## Facts on the pages (change them everywhere at once)

- Season 1: US$114,454 raised for Caring for Cambodia.
- Season 2: raising money for Lao Friends Hospital for Children, run by Friends Without A Border. It ends at IRONMAN 70.3 Western Australia in Busselton on 6 December 2026. The total shown is US$115,000, as at 9 November 2026.
- Facts appear in four places: the visible copy in index.html and about.html, the structured data (JSON-LD) in the head of index.html, llms.txt, and the share text in the `studs-config` block near the bottom of index.html.

## Common jobs

### Update the Season 2 total

1. Copy the current total from the GoFundMe page.
2. In index.html, find the comment `SEASON 2 TOTAL`. Change the figure and the "as at" date.
3. Change the same figure and date in llms.txt.

This touches no script, so no hash refresh is needed.

### Change some copy

Edit the text inside the right section of index.html or about.html. Keep headlines short: the big headlines are sized to fill their lines.

### Add or replace a photo

1. Get the original from the owner. Check that it is a real photo and that everyone in it is whole.
2. Cut it to one of the frame shapes and save it as a JPEG at about quality 78, without EXIF data (EXIF can hold the place it was taken):
   - portrait 3:4: 750 x 1000
   - upright 2:3: 667 x 1000
   - landscape 4:3: 1000 x 750
   - wide 3:2: 1000 x 667
   - tall: 800 x 1386 (used only for the Laguna runner)
3. Save it in public/images/ under a new file name (browsers keep images for a week): `training-*.jpg` for training, `race-*.jpg` for racing.
4. Add a figure to the shortest column of the right wall. Use the matching shape class and the file's width and height, and write alt text that says who is in it and what is happening, without names:

   ```html
   <figure class="wall-item plx landscape"><img src="images/training-new.jpg" width="1000" height="750" loading="lazy" decoding="async" alt="Four STUDS members riding along East Coast Park at dawn"></figure>
   ```

5. The frame's shape must match the file's shape, or people get cropped. tools/check_layout.py reports any cropped photo.

### Change the sponsors

The sponsors are in the footer of both pages (`<ul class="sponsors">`). Logos are white PNGs with a transparent background in public/images/sponsors/. Each has a width class (`.logo-boomarang`, `.logo-tsunami`) in the CSS of both pages, set by eye so the logos look the same size. Also update the sponsor list in the JSON-LD of index.html and in llms.txt.

### Edit a script

index.html has two inline scripts. The first is the Lenis smooth-scrolling library: leave it alone. The second runs the page. After any change to either one, even a single character, run:

```
python3 tools/update_csp.py
```

Otherwise browsers block the script on the live site, and the page loses its motion and its Share button. Edits to HTML or CSS don't need this. The JSON blocks (the structured data and `studs-config`) are not hashed.

## How the main page works

Sections in order: the hero ("Ordinary men."), the challenge (the STUDS acronym, the training wall, then "Race days." with the family photo and the race wall), the cause (the hospital), "Recovery drinks.", the season totals, "Every penny helps." (donate and share), and the footer.

- Motion: every movement follows the scroll position and runs in one animation loop (the "Motion" part of the second script). Visitors who ask their device for reduced motion get the same page without movement. With JavaScript off, they get a plain layout. The page's background colour fades from one section to the next.
- Big type on wide screens: the layout stops getting wider at 1440px. Big type on desktop uses `calc(var(--vu) * N)`, where `--vu` is 1vw capped at 14.4px, so it stops growing at the same point. Never size big text in plain `vw`: on wide monitors it outgrows its column and runs into the next block. That bug has happened once already.
- Photo walls (`.wall`): three `.wall-col` columns of `figure.wall-item`. The shape class on each figure sets the shape of its frame. On phones the script moves the third column's photos into the two columns shown (`arrangeWalls`). With motion on, the columns drift at different speeds and each photo opens from a slit.
- Recovery drinks: two `.social-row` groups. Each figure carries `style="--a: …"` with its photo's width divided by its height, so every desktop row fills the width with each photo whole. On phones the rows turn into a two-column mosaic.
- Photos fade from a navy tint to full colour as they scroll into view (`paintTint`).
- On phones, a floating Donate button appears once the hero has scrolled away. Share opens the phone's share menu, with Copy link as the fallback.

## Checking a change

1. Run `python3 tools/check_layout.py` (add `--all` to include Firefox and Safari's engine). It needs Playwright, and must end with "All clear."
2. Look at both pages on a real phone if you can.
3. If you changed a script, make sure tools/update_csp.py has run and the page still moves as you scroll.

## Publishing

- Netlify project: "studs-sg", site ID `c904b41a-d842-4734-82aa-f3e8372f083f`. Publish directory: `public`. No build command.
- The live address for now is https://studs-sg.netlify.app. studs.sg is set up in Netlify as the main domain but wasn't working yet: it was waiting on the .sg registry. Until it works, the links that have to be full addresses (canonical, link previews, structured data, sitemap.xml, robots.txt and llms.txt) use `https://studs-sg.netlify.app/`. Once studs.sg works, replace `https://studs-sg.netlify.app/` with `https://studs.sg/` in public/index.html, about.html, llms.txt, robots.txt and sitemap.xml, run tools/update_csp.py to be safe, and publish.
- Don't make studscharity.com or studsfoundation.com the main address while the charity registration is pending.
- To publish: if the site is in a GitHub repository linked to the Netlify project, push to the main branch. Otherwise drag the public folder onto the project's Deploys page in Netlify, or use the Netlify CLI: `netlify deploy --prod --dir public --site c904b41a-d842-4734-82aa-f3e8372f083f`.
- Afterwards, open the live site on a phone and a desktop and check that it loads and moves as you scroll.

## Decisions already made (don't undo them without asking)

- The "Join us" WhatsApp buttons were removed.
- Sponsors were cut to Boomarang and Tsunami. Cupcke and XXL Design & Construct were removed.
- A beach sunrise photo turned out to be AI-generated and was removed.
- Photo frames match the photos' shapes, and the drift inside frames that cut off people at the edges was removed.
- Big type is capped at the 1440px layout width.
- The hospital section comes after the STUDS section and before Recovery drinks.
