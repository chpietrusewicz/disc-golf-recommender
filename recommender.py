import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# 1. Load local JSON dataset (Mirrors the live API structure)
print("Loading local JSON dataset...")
with open('data/discs.json', 'r') as f:
    json_data = json.load(f)

# 2. Extract and flatten records (handles nested 'specs')
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

def parse_comparative_query(user_query, df):
    query_lower = user_query.lower()
    
    # Check if the user is comparing to a specific disc (e.g., "than a destroyer")
    match = re.search(r'than an?\s+([a-zA-Z0-9\s]+)', query_lower)
    
    if match:
        ref_disc_name = match.group(1).strip()
        
        # Find the reference disc in your DataFrame (case-insensitive search)
        ref_row = df[df['name'].str.lower() == ref_disc_name]
        
        if not ref_row.empty:
            ref_speed = ref_row.iloc[0]['speed']
            ref_fade = ref_row.iloc[0]['fade']
            ref_turn = ref_row.iloc[0]['turn']
            
            print(f"--> [Smart Parser] Found reference disc: {ref_row.iloc[0]['brand']} {ref_row.iloc[0]['name']} (Speed: {ref_speed}, Fade: {ref_fade})")
            
            # If they want something "more stable", look for higher fade or similar speed
            if "more stable" in query_lower or "beefier" in query_lower:
                filtered_df = (df['fade'] > ref_fade)
                return filtered_df
            if "less stable" in query_lower or "flippier" in query_lower:
                filtered_df = (df['turn'] < ref_turn)
                return filtered_df
                
    # Fallback: If no comparison pattern is found, return the full DataFrame
    return df

# 3. Build text profiles for TF-IDF matching
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
        profile += "fairway control"

    if glide >= 5:
        profile += " floaty glidey"
    else:
        profile += "gets down drops dead low-glide"

    return profile


df['profile'] = df.apply(make_profile, axis=1)

# 4. Vectorize text profiles
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(df['profile'])

# 5. Recommendation Function
def smart_recommend(user_query, df, top_n=3):
    # 1. Check if it's a comparative query and filter the dataset dynamically
    subset_df = parse_comparative_query(user_query, df)
    
    # If the smart parser filtered down our dataset, we vectorize only that subset
    # (Or you can combine it with TF-IDF scoring on the subset)
    if not subset_df.empty and len(subset_df) < len(df):
        # Return top matches from the mathematically filtered subset
        return subset_df[['brand', 'name', 'type', 'speed', 'fade']].head(top_n)
    
    query_vec = vectorizer.transform([user_query])
    scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
    top_indices = scores.argsort()[-top_n:][::-1]
    
    results = df.iloc[top_indices]
    return results[['brand', 'name', 'type', 'speed', 'thickness']]

# 6. Test it out
if __name__ == "__main__":
    test_query = "I want something flippier than a destroyer"
    print(f"\nQuery: '{test_query}'\n")
    print(smart_recommend(test_query, df, top_n=3))