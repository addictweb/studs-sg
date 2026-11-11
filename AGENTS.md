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
- Season numbers ("Season 1", "Season 2") appear only beside the money raised, in the totals section. Visitors don't care about them, so keep them out of page titles, headlines, copy, photo descriptions and share text.
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
tools/photo.py         prepares a new wall photo (all four files) and prints the markup to paste
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
2. Pick the frame shape closest to the photo, so nobody gets cut off: portrait (3:4), upright (2:3), landscape (4:3) or wide (3:2). (A fifth shape, tall, is used only for the Laguna runner.)
3. Run `python3 tools/photo.py <original> <new-name> <shape>`, for example `python3 tools/photo.py ~/Downloads/IMG_1234.jpg training-swim landscape`. Use a name that hasn't been used before (browsers keep images for a week): `training-*` for training, `race-*` for racing. It writes four files to public/images/ (full size and 600px wide, each as JPEG and WebP), strips the EXIF data (which can hold the place it was taken), and prints the markup.
4. Paste the markup into the shortest column of the right wall, and replace the alt text with a description of who is in the photo and what is happening, without names. The markup looks like this:

   ```html
   <figure class="wall-item plx landscape"><picture><source type="image/webp" srcset="images/training-swim-600.webp 600w, images/training-swim.webp 1000w" sizes="(min-width: 1440px) 384px, (min-width: 960px) 27vw, calc(50vw - 25px)"><img src="images/training-swim.jpg" srcset="images/training-swim-600.jpg 600w, images/training-swim.jpg 1000w" sizes="(min-width: 1440px) 384px, (min-width: 960px) 27vw, calc(50vw - 25px)" width="1000" height="750" loading="lazy" decoding="async" alt="Four STUDS members swimming at Sentosa at dawn"></picture></figure>
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
- Photo files: every photo is served as WebP, with the JPEG as a fallback, inside `<picture>`. Wall photos also have 600px-wide copies, which phones and ordinary screens use. Once the page has loaded, the script fetches the remaining photos quietly, three at a time, so they are ready before visitors scroll to them. Keep new photos to this pattern: the page was slow on phones when it sent full-size photos.
- On phones, a floating Donate button appears once the hero has scrolled away. Share opens the phone's share menu, with Copy link as the fallback.

## Checking a change

1. Run `python3 tools/check_layout.py` (add `--all` to include Firefox and Safari's engine). It needs Playwright, and must end with "All clear."
2. Look at both pages on a real phone if you can.
3. If you changed a script, make sure tools/update_csp.py has run and the page still moves as you scroll.

## Publishing

- Netlify project: "studs-sg", site ID `c904b41a-d842-4734-82aa-f3e8372f083f`. Publish directory: `public`. No build command.
- The address is https://studs.sg (www.studs.sg and studs-sg.netlify.app reach the same site). Netlify provides the security certificate and sends http visitors to https. Links that must be full addresses (canonical, link previews, structured data, sitemap.xml, robots.txt and llms.txt) use `https://studs.sg/`.
- Don't make studscharity.com or studsfoundation.com the main address while the charity registration is pending.
- The code is at https://github.com/addictweb/studs-sg. The Netlify project publishes its main branch, so a push to main changes the live site: ask the owner before pushing. Work on another branch if a change isn't ready.
- Other people can edit by being added as collaborators on the GitHub repository; they never need the owner's Netlify login. On Netlify's free plan this only works while the repository stays public.
- Without GitHub: drag the public folder onto the project's Deploys page in Netlify, or use the Netlify CLI: `netlify deploy --prod --dir public --site c904b41a-d842-4734-82aa-f3e8372f083f`.
- Afterwards, open the live site on a phone and a desktop and check that it loads and moves as you scroll.

## Decisions already made (don't undo them without asking)

- The "Join us" WhatsApp buttons were removed.
- Sponsors were cut to Boomarang and Tsunami. Cupcke and XXL Design & Construct were removed.
- A beach sunrise photo turned out to be AI-generated and was removed.
- Photo frames match the photos' shapes, and the drift inside frames that cut off people at the edges was removed.
- Big type is capped at the 1440px layout width.
- The hospital section comes after the STUDS section and before Recovery drinks.
- The browser tab title is "STUDS | Ordinary men, extraordinary challenges" (the About page: "About STUDS | Ordinary men, extraordinary challenges").
- "Season 2" was taken out of the page title, the hero, the Busselton line, the photo descriptions and the About page. Season numbers now appear only on the totals.
- Photos are WebP with JPEG fallbacks, with 600px copies of the wall photos, and the rest are fetched in the background after the page loads. This cut a phone visit from about 4.2 MB of photos to under 2 MB.
