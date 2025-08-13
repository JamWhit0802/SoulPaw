from django.shortcuts import render, HttpResponse
import requests
from django.core.paginator import Paginator
import os
from django.conf import settings

def normalize_location(loc):
    if not loc:
        return ""
    loc = str(loc).strip()
    if loc.lower() in ("", "unknown", "n/a", "none"):
        return ""
    return loc

def dog_matches(request):
    url = "https://api.rescuegroups.org/v5/public/animals/search"

    headers = {
        "Content-Type": "application/vnd.api+json", 
        "Authorization": settings.RESCUEGROUPS_API_KEY
    }

    filters = [
        {"fieldName": "species.singular", "operation": "equals", "criteria": "Dog", "available": "true"}
    ]

    payload = {
        "data": {
            "filters": filters,
            "filterRadius": {
                "postalcode": "60601",
                "miles": 50
            },
            "include": ["pictures", "orgs"],
            "fields": {
                "animals": ["name", "breedPrimary", "ageGroup"],
                "pictures": ["large"],
                "orgs": ["name", "city", "state", "url"]
            },
            "page": {
                "limit": 30,
                "offset": 0
            },
            "sort": ["distance"]
        }
    }

    response = requests.post(url, json=payload, headers=headers)
    print("API STATUS:", response.status_code)

    animals = []
    try:
        data = response.json()

        included_pics = {p["id"]: p for p in data.get("included", []) if p.get("type") == "pictures"}
        included_orgs = {o["id"]: o for o in data.get("included", []) if o.get("type") == "orgs"}

        for item in data.get("data", []):
            attributes = item.get("attributes", {})
            relationships = item.get("relationships", {})

            # Get picture
            pic_url = ""
            pic_ids = relationships.get("pictures", {}).get("data", [])
            if pic_ids:
                first_id = pic_ids[0].get("id")
                pic_attr = included_pics.get(first_id, {}).get("attributes", {})
                pic_url = pic_attr.get("large", {}).get("url") or ""

            # Get org location
            org_name = ""
            location = ""
            org_ids = relationships.get("orgs", {}).get("data", [])
            if org_ids:
                first_org_id = org_ids[0].get("id")
                org_attr = included_orgs.get(first_org_id, {}).get("attributes", {})
                org_name = org_attr.get("name", "")
                city = org_attr.get("city", "")
                state = org_attr.get("state", "")
                if city and state:
                    location = f"{city}, {state}"

            animals.append({
                "id": item.get("id"),
                "name": attributes.get("name", "Unknown"),
                "breed": attributes.get("breedPrimary", "Unknown"),
                "age": attributes.get("ageGroup", "Unknown"),
                "location": location or "Unknown",
                "organization": {"name": org_name},
                "image_url": pic_url
            })

    except Exception as e:
        print("Error parsing API response:", e)

    animals = filter_dogs(animals)
    return render(request, "dog-matches.html", {"dogs": animals})


def filter_dogs(animals):
    # add normalized location and org name to each dog (so sorting is stable & testable)
    for d in animals:
        d["location_norm"] = normalize_location(d.get("location"))
        # organization may be nested dict; handle missing safely
        org = d.get("organization") or {}
        d["org_name"] = (org.get("name") or org.get("organizationName") or "").strip()

    # debug: show first 6 locations before sort
    print("Before sort (first 6):", [(a.get("name"), a.get("location")) for a in animals[:6]])

    # Put dogs that HAVE a location first; then sort by location_norm then org_name
    known = [d for d in animals if d["location_norm"]]
    unknown = [d for d in animals if not d["location_norm"]]

    known.sort(key=lambda d: (d["location_norm"].lower(), d["org_name"].lower()))
    result = known + unknown

    # debug: show after sort (first 6)
    print("After sort (first 6):", [(a.get("name"), a.get("location_norm"), a.get("org_name")) for a in result[:6]])
    return result

def dog_details(request, animal_id):
    url = f"https://api.rescuegroups.org/v5/public/animals/{animal_id}"

    headers = {
        "Content-Type": "application/vnd.api+json",
        "Authorization": settings.RESCUEGROUPS_API_KEY
    }

    filters = [
        {"fieldName": "species.singular", "operation": "equals", "criteria": "Dog", "available": "true"}]

    payload = {
        "data": {
            "filters": filters,
            "filterRadius": {
                "postalcode": "60601",
                "miles": 50
            },
            "include": ["pictures", "orgs"],
            "fields": {
                "animals": ["name", "breedPrimary", "ageGroup"],
                "pictures": ["large"],
                "orgs": ["name", "city", "state", "url"]
            },
            "page": {
                "limit": 100,
                "offset": 0
            },
            "sort": ["distance"]
        }
    }


    response = requests.get(url, json=payload, headers=headers)
    print("DETAIL API STATUS:", response.status_code)
    print(response.text)

    if response.status_code != 200:
        payload = {"data": {"id": animal_id}}
        response = requests.post("https://api.rescuegroups.org/v5/public/animals/read", json=payload, headers=headers)

    animal = []
    try:
        data = response.json()
        included_pics = {p["id"]: p for p in data.get("included", []) if p.get("type") == "pictures"}
        included_orgs = {o["id"]: o for o in data.get("included", []) if o.get("type") == "orgs"}

        for item in data.get("data", []):
            attributes = item.get("attributes", {})
            relationships = item.get("relationships", {})
            pic_url = ""
            org_name = ""
            org_url = ""

            pic_ids = relationships.get("pictures", {}).get("data",{})
            org_ids = relationships.get("orgs", {}).get("data", [])
            if pic_ids:
                first_id = pic_ids[0].get("id")
                pic_attr = included_pics.get(first_id, {}).get("attributes", {})
                pic_url = pic_attr.get("large", {}).get("url") or pic_attr.get("original", {}).get("url", "")
            if org_ids:
                first_org_id = org_ids[0].get("id")
                org_attr = included_orgs.get(first_org_id, {}).get("attributes", {})
                org_name = org_attr.get("name", "")
                org_url = org_attr.get("url", "")
                city = org_attr.get("city", "")
                state = org_attr.get("state", "")
                if city and state:
                    location = f"{city}, {state}"


            animal.append({
                "id": item.get("id"), 
                "name": attributes.get("name", "Unknown"),
                "breed": attributes.get("breedPrimary", "Unknown"),
                "age": attributes.get("ageGroup", "Unknown"),
                "location": location or "Unknown",
                "organization": {"name": org_name , "url" : org_url},
                "image_url": pic_url
            })
    except Exception as e:
        print("Error parsing animal detail:", e)

    
    return render(request, "dog-details.html", {"dogs": animal})

def intro(request):
    return render(request, "intro.html")

def questionnaire(request):
    return render(request, "questionnaire.html")

