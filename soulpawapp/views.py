from django.shortcuts import render, HttpResponse
import requests
from django.core.paginator import Paginator
import os
from django.conf import settings


def dog_matches(request):
    url = "https://api.rescuegroups.org/v5/public/animals/search"

    headers = {
        "Content-Type": "application/vnd.api+json", 
        "Authorization": settings.RESCUEGROUPS_API_KEY
    }

    filters = [
        {"fieldName": "species.singular", "operation": "equals", "criteria": "Dog"}
    ]


    payload = {
    "data": {
        "filters": filters,
        "filterRadius": {
            "postalcode": "60601",  
            "miles": 50
        },
        "limit": 10,
        "sort": ["distance"],
        "include": ["pictures"],
        "fields": {
            "animals": ["name", "breedPrimary", "ageGroup", "location"],
            "pictures": ["large"]
        }
    }
}

    
    response = requests.post(url, json=payload, headers=headers)
    print("API STATUS:", response.status_code)
    print("RESPONSE TEXT:", response.text)

    
    animals = []

    try:
        data = response.json()
        included_pics = {p["id"]: p for p in data.get("included", []) if p.get("type") == "pictures"}

        for item in data.get("data", []):
            attributes = item.get("attributes", {})
            relationships = item.get("relationships", {})
            pic_url = ""

            pic_ids = relationships.get("pictures", {}).get("data", [])
            if pic_ids:
                first_id = pic_ids[0].get("id")
                pic_attr = included_pics.get(first_id, {}).get("attributes", {})
                pic_url = pic_attr.get("large", {}).get("url") or pic_attr.get("original", {}).get("url", "")

            animals.append({
                "id": item.get("id"), 
                "name": attributes.get("name", "Unknown"),
                "breed": attributes.get("breedPrimary", "Unknown"),
                "age": attributes.get("ageGroup", "Unknown"),
                "location": attributes.get("location", "Unknown"),
                "image_url": pic_url
            })

    except Exception as e:
        print("Error parsing API response:", e)
        

    return render(request, "dog-matches.html", {"dogs": animals})

def dog_details(request, animal_id):
    url = f"https://api.rescuegroups.org/v5/public/animals/{animal_id}"

    headers = {
        "Content-Type": "application/vnd.api+json",
        "Authorization": settings.RESCUEGROUPS_API_KEY
    }

    params = {
        "include": "pictures, organization"
    }

    response = requests.get(url, headers=headers, params=params)
    print("DETAIL API STATUS:", response.status_code)

    if response.status_code != 200:
        payload = {"data": {"id": animal_id}}
        response = requests.post("https://api.rescuegroups.org/v5/public/animals/read", json=payload, headers=headers)

    animal = {}
    try:
        data = response.json()
        item = data.get("data") if isinstance(data.get("data"), dict) else (data.get("data", [None])[0] if data.get("data") else None)

        if item:
            attr = item.get("attributes", {})
            included = data.get("included", [])
            pics = [p for p in included if p.get("type") == "pictures"]
            picture_urls = []
            for p in pics:
                a = p.get("attributes", {})
                url_large = a.get("large", {}).get("url")
                url_orig = a.get("original", {}).get("url")
                if url_large:
                    picture_urls.append(url_large)
                elif url_orig:
                    picture_urls.append(url_orig)

            org_data = next((i for i in included if i.get("type") == "organizations"), None)
            org_attr = org_data.get("attributes", {}) if org_data else {}

            animal = {
                "id": item.get("id"),
                "name": attr.get("name"),
                "breed": attr.get("breedPrimary"),
                "age": attr.get("ageGroup"),
                "sex": attr.get("sex"),
                "size": attr.get("sizeGroup"),
                "status": attr.get("status"),
                "location": attr.get("location"),
                "description": attr.get("descriptionPlain") or attr.get("description") or "",
                "pictures": picture_urls,
                "organization": {
                    "name": org_attr.get("name"),
                    "website": org_attr.get("websiteUrl"),
                    "adoption_process": org_attr.get("adoptionProcess"),
                    "facebook": org_attr.get("facebookUrl")
                }           

            }
    except Exception as e:
        print("Error parsing animal detail:", e)

    return render(request, "dog-details.html", {"dog": animal})

def intro(request):
    return render(request, "intro.html")

def questionnaire(request):
    return render(request, "questionnaire.html")

