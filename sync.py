import sys
import os
from bs4 import BeautifulSoup
from slugify import slugify  # pip install python-slugify

def read_html(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

def write_html(filename, content, dry_run=False):
    if dry_run:
        print(f"[DRY-RUN] Would write updated content to {filename}")
    else:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

def update_aside(soup, links):
    aside = soup.find("aside", class_="sidebar")
    if not aside:
        return
    ul = aside.find("ul")
    if not ul:
        return
    ul.clear()
    for href, text in links:
        li = soup.new_tag("li")
        a = soup.new_tag("a", href=href)
        a.string = text
        li.append(a)
        ul.append(li)

def main():
    if len(sys.argv) < 2:
        print("Usage: python update_site.py <new_homepage_filename> [--dry-run]")
        sys.exit(1)

    new_homepage_file = f"public/{sys.argv[1]}"
    new_homepage_filename = f"{sys.argv[1]}"
    dry_run = "--dry-run" in sys.argv

    index_file = "public/index.html"
    index_filename = "index.html"

    # Step 1: Rename old index.html
    old_homepage_html = read_html(index_file)
    old_homepage_soup = BeautifulSoup(old_homepage_html, "html.parser")
    old_title = old_homepage_soup.find("h1").get_text(strip=True)
    old_slug = slugify(old_title)
    old_homepage_file = f"public/{old_slug}.html"
    old_homepage_filename = f"{old_slug}.html"

    if dry_run:
        print(f"[DRY-RUN] Would rename {index_file} → {old_homepage_file}")
    else:
        os.rename(index_file, old_homepage_file)

    # Step 2: Rename new homepage to index.html
    if dry_run:
        print(f"[DRY-RUN] Would rename {new_homepage_file} → {index_file}")
    else:
        os.rename(new_homepage_file, index_file)

    # Step 3: Update old homepage aside
    new_homepage_html = read_html(new_homepage_file if dry_run else index_file)
    new_homepage_soup = BeautifulSoup(new_homepage_html, "html.parser")
    new_title = new_homepage_soup.find("h1").get_text(strip=True)

    links_old = [(f"public/index.html", new_title)] + [
        (a["href"], a.get_text(strip=True))
        for a in old_homepage_soup.select("aside.sidebar ul li a")
    ]
    update_aside(old_homepage_soup, links_old)
    if dry_run:
        print(f"[DRY-RUN] Would update {old_homepage_file} aside to:")
        for href, text in links_old:
            print(f"   {text} → {href}")
    else:
        write_html(old_homepage_file, str(old_homepage_soup))

    # Step 4: Update new homepage aside
    links_new = [(f"/{old_homepage_file}", old_title)] + [
        (a["href"], a.get_text(strip=True))
        for a in old_homepage_soup.select("aside.sidebar ul li a")[1:]
    ]
    update_aside(new_homepage_soup, links_new)
    if dry_run:
        print(f"[DRY-RUN] Would update {index_file} aside to:")
        for href, text in links_new:
            print(f"   {text} → {href}")
    else:
        write_html(index_file, str(new_homepage_soup))

    # Step 5 & 6: Update other pages
    for fname in os.listdir("public"):
        if not fname.endswith(".html"):
            continue
        if fname in [index_filename, old_homepage_filename, new_homepage_filename]:
            continue

        html = read_html(f"public/{fname}")
        soup = BeautifulSoup(html, "html.parser")
        aside = soup.find("aside", class_="sidebar")
        if aside:
            links = [(a["href"], a.get_text(strip=True)) for a in aside.select("ul li a")]

            # Normalize href for matching
            new_links = []
            inserted_old_homepage = False
            for href, text in links:
                clean_href = href.lstrip("./")  # remove ./ or /
                if clean_href in ["index.html"]:
                    # Update homepage link text
                    new_links.append(("/index.html", new_title))
                    # Insert old homepage link right after
                    new_links.append((f"/{old_homepage_file}", old_title))
                    inserted_old_homepage = True
                else:
                    new_links.append((href, text))

            # If homepage link not found, prepend both
            if not inserted_old_homepage:
                new_links.insert(0, ("/index.html", new_title))
                new_links.insert(1, (f"/{old_homepage_file}", old_title))

            update_aside(soup, new_links)

            if dry_run:
                print(f"[DRY-RUN] Would update {fname} aside to:")
                for href, text in new_links:
                    print(f"   {text} → {href}")
            else:
                write_html(f"public/{fname}", str(soup))

    print("Dry-run complete." if dry_run else "Site update complete.")

if __name__ == "__main__":
    main()
