import sys, re, csv, requests
import pandas as pd
from os import path

def combine_wiki_tables(url_base, page):
    url = f"{url_base}/{page}"
    html = requests.get(url).content
    df_list = pd.read_html(html)

    dfs = []
    for df in df_list[5:]:
        # Handle tables with multiple header rows, i.e. Gates
        if not isinstance(df.columns[0], str):
            df.columns = [multicols[-1] for multicols in df.columns]
        df = df.replace("\xa0", " ", regex=True)
        dfs.append(df[["Name", "Ingredients"]])
    combined_df = pd.concat(dfs, ignore_index=True)
    return combined_df

def save_csv(data, filename):
    if isinstance(data, pd.DataFrame):
        data.to_csv(filename, encoding='utf-8')
        return
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)

def read_csv(filename):
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        data = list(reader)
    return data

def parse_data(data):
    out = {}
    
    for line in data[1:]:
        item = line[1]
        groups = re.findall(r" ?([a-zA-Z\(\) ]*) \((\d+)\)", line[2])
        
        for i, count in groups:
            ingredient = i.strip()
            if ingredient not in out:
                out[ingredient] = []
            out[ingredient].append((item, count))

    return sorted(out.items(), key=lambda x: len(x[1]), reverse=True)

def main(page, url="https://stardewvalleywiki.com"):
    filename = f"{page}.src"

    if not path.exists(filename):
        df = combine_wiki_tables(url, page)
        save_csv(df, filename)
    data = read_csv(filename)
    parsed = parse_data(data)
    
    save_csv(parsed, f"{page}_combined.csv")
    save_csv([(i, len(e)) for i, e in parsed], f"{page}_counts.csv")

if __name__ == "__main__":
    page = "Crafting"
    sys.exit(main(page))