import json
import shutil
import uuid
from pathlib import Path


ROOT = Path(r"C:\Users\User\Documents\Codex\2026-11-06\microsoft-power-bi-plugin-power-bi-2\outputs\Products_Dashboard")
REPORT_DEF = ROOT / "Products.Report" / "definition"
PAGES_DIR = REPORT_DEF / "pages"
MODEL_PRODUCTS = ROOT / "Products.SemanticModel" / "definition" / "tables" / "Products.tmdl"
DATA = ROOT / "cleaned_data.csv"


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def col(entity: str, prop: str):
    return {
        "Column": {
            "Expression": {"SourceRef": {"Entity": entity}},
            "Property": prop,
        }
    }


def measure(prop: str):
    return {
        "Measure": {
            "Expression": {"SourceRef": {"Entity": "Products"}},
            "Property": prop,
        }
    }


def projection(field, query_ref: str, native_ref: str | None = None):
    result = {"field": field, "queryRef": query_ref, "nativeQueryRef": native_ref or query_ref.split(".")[-1]}
    if "Column" in field:
        result["active"] = True
    return result


def title_object(text: str):
    return {
        "title": [
            {
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'" + text.replace("'", "''") + "'"}}},
                }
            }
        ]
    }


def new_visual(page_id: str, visual_type: str, title: str, x: int, y: int, w: int, h: int,
               category=None, value=None, slicer=None, tab=0):
    visual_id = uuid.uuid4().hex[:20]
    state = {}
    if slicer:
        state["Values"] = {"projections": [projection(col(*slicer), f"{slicer[0]}.{slicer[1]}")]}
    elif visual_type == "card":
        state["Values"] = {"projections": [projection(measure(value), f"Products.{value}")]}
    else:
        if category:
            state["Category"] = {"projections": [projection(col(*category), f"{category[0]}.{category[1]}")]}
        state["Y"] = {"projections": [projection(measure(value), f"Products.{value}")]}

    visual = {
        "visualType": visual_type,
        "query": {"queryState": state},
        "objects": title_object(title),
        "drillFilterOtherVisuals": True,
    }
    if category and not slicer:
        visual["query"]["queryState"]["Category"]["projections"][0]["active"] = True
        visual["query"]["sortDefinition"] = {
            "sort": [{"field": measure(value), "direction": "Descending"}],
            "isDefaultSort": True,
        }

    obj = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json",
        "name": visual_id,
        "position": {"x": x, "y": y, "z": tab, "height": h, "width": w, "tabOrder": tab},
        "visual": visual,
    }
    if category and not slicer:
        obj["filterConfig"] = {"filters": [
            {"name": uuid.uuid4().hex[:20], "field": col(*category), "type": "Categorical"},
            {"name": uuid.uuid4().hex[:20], "field": measure(value), "type": "Advanced"},
        ]}
    write_json(PAGES_DIR / page_id / "visuals" / visual_id / "visual.json", obj)


def clear_page_visuals(page_id: str):
    visuals = PAGES_DIR / page_id / "visuals"
    if visuals.exists():
        shutil.rmtree(visuals)
    visuals.mkdir(parents=True)


def make_page(page_id: str, display_name: str):
    write_json(PAGES_DIR / page_id / "page.json", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
        "name": page_id,
        "displayName": display_name,
        "displayOption": "FitToPage",
        "height": 1080,
        "width": 1920,
    })
    clear_page_visuals(page_id)


def main():
    executive = "fe8829640ac3b94e2ca3"
    category_page = "2ee61c5005d701d42237"
    pricing_page = uuid.uuid4().hex[:20]

    make_page(executive, "Executive Overview")
    make_page(category_page, "Category & Brand")
    make_page(pricing_page, "Pricing & Customer")

    # Executive page: compact filter rail, KPI strip, and trends/drivers.
    for i, (field, x) in enumerate([(("Dim_Date", "Year Month"), 20), (("Products", "Category"), 340), (("Products", "Brand"), 660)]):
        new_visual(executive, "slicer", field[1], x, 18, 300, 78, slicer=field, tab=i)
    for i, (metric, label) in enumerate([
        ("Total Revenue", "Revenue"),
        ("Total Units Sold", "Units Sold"),
        ("Total Products", "Products"),
        ("Average Rating", "Average Rating"),
    ]):
        new_visual(executive, "card", label, 20 + i * 470, 112, 450, 150, value=metric, tab=3 + i)
    new_visual(executive, "lineChart", "Revenue by Month", 20, 282, 950, 345,
               category=("Dim_Date", "Year Month"), value="Total Revenue", tab=7)
    new_visual(executive, "clusteredBarChart", "Revenue by Category", 990, 282, 910, 345,
               category=("Products", "Category"), value="Total Revenue", tab=8)
    new_visual(executive, "clusteredBarChart", "Revenue by Brand", 20, 642, 930, 395,
               category=("Products", "Brand"), value="Total Revenue", tab=9)
    new_visual(executive, "clusteredBarChart", "Average Discount by Competitor", 970, 642, 930, 395,
               category=("Products", "Competitor"), value="Average Discount %", tab=10)

    # Category page: compare sales, volume, and assortment across category/brand.
    for i, (field, x) in enumerate([(("Dim_Date", "Year Month"), 20), (("Products", "Category"), 340), (("Products", "Brand"), 660)]):
        new_visual(category_page, "slicer", field[1], x, 18, 300, 78, slicer=field, tab=i)
    new_visual(category_page, "clusteredBarChart", "Revenue by Category", 20, 120, 930, 390,
               category=("Products", "Category"), value="Total Revenue", tab=3)
    new_visual(category_page, "clusteredBarChart", "Units Sold by Category", 970, 120, 930, 390,
               category=("Products", "Category"), value="Total Units Sold", tab=4)
    new_visual(category_page, "clusteredBarChart", "Revenue by Brand", 20, 530, 930, 500,
               category=("Products", "Brand"), value="Total Revenue", tab=5)
    new_visual(category_page, "clusteredBarChart", "Product Count by Brand", 970, 530, 930, 500,
               category=("Products", "Brand"), value="Total Products", tab=6)

    # Pricing and customer page: price position, ratings, reviews and discount levels.
    for i, (field, x) in enumerate([(("Dim_Date", "Year Month"), 20), (("Products", "Category"), 340), (("Products", "Competitor"), 660)]):
        new_visual(pricing_page, "slicer", field[1], x, 18, 300, 78, slicer=field, tab=i)
    new_visual(pricing_page, "clusteredBarChart", "Average Price by Category", 20, 120, 930, 390,
               category=("Products", "Category"), value="Average Price", tab=3)
    new_visual(pricing_page, "clusteredBarChart", "Average Rating by Category", 970, 120, 930, 390,
               category=("Products", "Category"), value="Average Rating", tab=4)
    new_visual(pricing_page, "clusteredBarChart", "Discount Rate by Competitor", 20, 530, 930, 500,
               category=("Products", "Competitor"), value="Average Discount %", tab=5)
    new_visual(pricing_page, "clusteredBarChart", "Review Volume by Brand", 970, 530, 930, 500,
               category=("Products", "Brand"), value="Total Reviews", tab=6)

    write_json(PAGES_DIR / "pages.json", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json",
        "pageOrder": [executive, category_page, pricing_page],
        "activePageName": executive,
    })

    # Make the copied project self-contained by pointing the import query to its bundled CSV.
    m = MODEL_PRODUCTS.read_text(encoding="utf-8")
    old = 'File.Contents("C:\\Users\\User\\Downloads\\cleaned_data.csv")'
    replacement = 'File.Contents("' + str(DATA) + '")'
    if old not in m:
        raise RuntimeError("Expected source path was not present in the copied model.")
    MODEL_PRODUCTS.write_text(m.replace(old, replacement), encoding="utf-8")

    # Remove the unused scaffold page folder from the copied report.
    for child in PAGES_DIR.iterdir():
        if child.is_dir() and child.name not in {executive, category_page, pricing_page}:
            shutil.rmtree(child)
    print(json.dumps({"pages": [executive, category_page, pricing_page], "visuals": 25, "data": str(DATA)}))


if __name__ == "__main__":
    main()
