# Optional: stock images (Pexels / Pixabay)

**The client's own photos come first.** They are the brand. Use stock only when there's a real gap: a category with no photo, a neighbourhood or scene the site doesn't show, a background texture.

## When to offer it
In the first reply, mention it as **optional**: "If you want extra imagery, a free Pexels or Pixabay API key lets me pull matching photos". Offer it again at G2b if the photo inventory is thin. Don't push it when the site already has enough imagery.

## Keys (both free)
- `PEXELS_API_KEY`: https://www.pexels.com/api/
- `PIXABAY_API_KEY`: https://pixabay.com/api/docs/

Put them in the environment or `.env`, like the other keys.

## Use
```bash
python scripts/fetch_stock.py "dog walker city street evening" assets/img/stock --n 6 --source both
```
- It writes the images plus `credits.json` (source, author, page, licence).
- Write precise queries that describe the shot, not the concept.
- Pull a few candidates, look at them, keep only those that match the design system's grade and composition.

## Rules
- **Licences:**
  - Pexels License and Pixabay Content License allow commercial use without payment;
  - credit is appreciated, so add a credits line in the delivery note (and in the video description when published).
- **Avoid:**
  - visible third-party brands or logos;
  - recognisable people in a way that implies they endorse the client;
  - images that misrepresent the client's actual service or location.
- **Grade everything the same way** (CSS filter or FFmpeg), so stock and client photos read as one set.
- Keep `credits.json` with the project and never commit the keys.
