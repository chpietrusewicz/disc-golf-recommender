import os
import requests
import json
import pandas as pd
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

load_dotenv()

API_KEY = os.getenv("TRYDISCS_API_KEY")

#Case insensitive set of recommended brands for filtering
RECOMMENDED_BRANDS = [
    "Innova",
    "Discraft",
    "Dynamic Discs",
    "MVP",
    "Axiom",
    "Latitude 64",
    "Westside",
    "Prodigy",
    "Gateway",
    "Discmania",
    "Kastaplast"
]

if not API_KEY:
    raise ValueError("API key missing! Make sure TRYDISCS_API_KEY is set in your .env file.")

print("Fetching live disc data from Try Discs API...")
url = "https://api.trydiscs.com/v1/discs?limit=2500"

headers = {
    "X-API-Key": API_KEY
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    json_data = response.json()
    print("Successfully fetched JSON response from API!")
else:
    print(f"API Request Failed ({response.status_code}): {response.text}")
    exit()

discs_list = json_data.get('data', [])
flattened_data = []

for disc in discs_list:
    specs = disc.get('specs', {})
    flattened_data.append({
        'brand': disc.get('brand'),
        'name': disc.get('name'),
        'type': disc.get('type'),
        'speed': disc.get('speed'),
        'glide': disc.get('glide'),
        'turn': disc.get('turn'),
        'fade': disc.get('fade'),
        'stability': disc.get('stability'),
        'bead': disc.get('bead'),
        'discontinued': disc.get('discontinued'),
        'diameter': specs.get('diameter_cm'),
        'height': specs.get('height_cm'),
        'depth': specs.get('rim_depth_cm'),
        'thickness': specs.get('rim_thickness_cm'),
        'inside_diameter': specs.get('inside_rim_diameter_cm'),
        'rim_depth_diameter_ratio': specs.get('rim_depth_diameter_ratio'),
        'rim_configuration': specs.get('rim_configuration'),
    })

df = pd.DataFrame(flattened_data)

df = df[df['discontinued'] == False]
if RECOMMENDED_BRANDS:
    allowed_brands = {brand.casefold() for brand in RECOMMENDED_BRANDS}
    df = df[df['brand'].fillna('').str.casefold().isin(allowed_brands)]

def parse_comparative_query(user_query, df):
    query_lower = user_query.lower()
    
    match = re.search(
        r'(?:than an?\s+|as (?:an?\s+|the\s+))'
        r'([a-zA-Z0-9][a-zA-Z0-9\s-]*?)\s*$',
        query_lower,
    )
    
    if match:
        ref_disc_name = match.group(1).strip()
        
        ref_row = df[df['name'].str.lower() == ref_disc_name]
        
        if not ref_row.empty:
            ref_speed = ref_row.iloc[0]['speed']
            ref_fade = ref_row.iloc[0]['fade']
            ref_turn = ref_row.iloc[0]['turn']
            
            print(f"--> [Smart Parser] Found reference disc: {ref_row.iloc[0]['brand']} {ref_row.iloc[0]['name']} (Speed: {ref_speed}, Fade: {ref_fade})")

            filtered_df = df
            
            if "faster" in query_lower:
                filtered_df = filtered_df.loc[filtered_df['speed'] > ref_speed]
            if "slower" in query_lower:
                filtered_df = filtered_df.loc[filtered_df['speed'] < ref_speed]
            if "more stable" in query_lower or "beefier" in query_lower:
                filtered_df = filtered_df.loc[filtered_df['fade'] > ref_fade]
            if "less stable" in query_lower or "flippier" in query_lower:
                filtered_df = filtered_df.loc[filtered_df['turn'] < ref_turn]
            if "straighter" in query_lower:
                filtered_df = filtered_df.loc[
                    (filtered_df['turn'] + filtered_df['fade']).abs()
                    < abs(ref_turn + ref_fade)
                ]
            if "same speed" in query_lower:
                filtered_df = filtered_df.loc[filtered_df['speed'] == ref_speed]

            return filtered_df
                
    return df

def make_profile(row):
    turn = row['turn']
    fade = row['fade']
    speed = row['speed']
    glide = row['glide']

    profile = (
        f"{row['brand']} {row['name']} {row['type']}. "
        f"Speed {row['speed']}, glide {row['glide']}, turn {row['turn']}, fade {row['fade']}. "
    )

    if turn + fade >= 2:
        profile += "overstable beefy reliable wind resistant headwind torque resistant hyzer finishes hard"
    elif turn + fade <= -2:
        profile += "understable flippy easy to throw beginner friendly tailwind turnover hyzer flip roller"
    else:
        profile += "stable neutral straight"

    if speed >= 11:
        profile += "fast power distance big arm driver max distance maximum"
    elif speed <= 5:
        profile += "slow putter approach midrange easy to throw low arm speed"
    else:
        profile += "fairway control not too far"

    if glide >= 4:
        profile += " floaty glidey"
    elif glide <= 2:
        profile += "gets down drops dead low-glide goes nowhere"

    return profile


df['profile'] = df.apply(make_profile, axis=1)

vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(df['profile'])

# 5. Recommendation Function
def smart_recommend(user_query, df, top_n=3):
    # Filter once for hard comparison constraints, then rank only those
    # candidates using the complete query and normal TF-IDF parsing.
    subset_df = parse_comparative_query(user_query, df)
    if subset_df.empty:
        return subset_df[['brand', 'name', 'type', 'speed', 'glide', 'turn', 'fade']]

    query_vec = vectorizer.transform([user_query])
    candidate_matrix = vectorizer.transform(subset_df['profile'])
    scores = cosine_similarity(query_vec, candidate_matrix).flatten()
    top_indices = scores.argsort()[-top_n:][::-1]
    
    results = subset_df.iloc[top_indices]
    return results[['brand', 'name', 'type', 'speed', 'glide', 'turn', 'fade']]

if __name__ == "__main__":
    test_query = "i want something straight from MVP that is easy to throw"
    print(f"\nQuery: '{test_query}'\n")
    print(smart_recommend(test_query, df, top_n=3))