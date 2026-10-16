# 🥏 Discwise

A natural-language disc golf recommender that helps players find discs based on the flight characteristics they want.

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-Recommendation%20System-orange?logo=scikit-learn)
![Try Discs API](https://img.shields.io/badge/Data-Try%20Discs%20API-green)

## Overview

Choosing a disc can be difficult, especially when players describe what they want using terms like “flippy,” “straight,” “overstable,” or “easy to throw” instead of specific flight numbers.

Discwise solves this problem by allowing users to describe the type of disc they want in plain English. The application combines disc flight numbers, generated disc profiles, brand preferences, and natural-language similarity to recommend discs that match the user's request.

The application also supports comparison-based searches, such as finding a disc that is faster than a Destroyer or more stable than another disc.

## Key Features

- 🔎 Search for discs using natural-language descriptions
- 🏷️ Filter recommendations by brand
- 📊 Compare flight numbers including:
  - Speed
  - Glide
  - Turn
  - Fade
- 🧠 Rank recommendations using TF-IDF and cosine similarity
- ⚡ Support comparative queries such as:
  - Faster than a specific disc
  - Slower than a specific disc
  - More stable than a specific disc
  - Less stable than a specific disc
  - Straighter than a specific disc
  - The same speed as a specific disc
- 📱 Responsive frontend for desktop and mobile devices
- 🔄 Fetch live disc information from the Try Discs API
- 📋 Display up to six recommended discs with their flight numbers
- ✅ Filter out discontinued discs
- 🎯 Include recommendations from selected disc brands

## Tech Stack

- 🐍 Python for the backend and recommendation logic
- 🌐 HTML for the application structure
- 🎨 CSS for styling and responsive layout
- ⚡ JavaScript for frontend interactions
- 🧮 Pandas for organizing and processing disc data
- 🤖 Scikit-learn for TF-IDF vectorization and cosine similarity
- 🔌 Try Discs API for disc information
- 🔐 python-dotenv for loading environment variables
- 📡 Python `http.server` for serving the application and API endpoints

## Getting Started

### Prerequisites

Before running the application, make sure you have:

- Python 3 installed
- A Try Discs API key
- `pip` installed

### Clone the Repository

```bash
git clone https://github.com/chpietrusewicz/disc-golf-recommender.git
cd disc-golf-recommender
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure the API Key

Create a `.env` file in the root directory:

```env
TRYDISCS_API_KEY=your_api_key_here
```

The application uses this key to retrieve disc data from the Try Discs API.

### Run the Application

```bash
python server.py
```

The application will be available at:

```text
http://127.0.0.1:8000
```

### Use the Application

1. Select one or more disc brands.
2. Describe the type of disc you want.
3. Choose an example query or enter your own.
4. Click **Find my discs**.
5. Review the recommended discs and their flight numbers.

Example searches:

```text
Something straight and easy to throw
```

```text
A flippy fairway driver
```

```text
Something faster than a Destroyer
```

## Engineering Challenges & Learnings

### Translating Natural Language into Recommendations

One of the main challenges was converting informal disc golf descriptions into useful recommendations. Players may use terms such as “flippy,” “beefy,” “straight,” or “easy to throw” instead of directly providing flight numbers.

To address this, the application creates a profile for each disc and adds descriptive terms based on its flight characteristics. For example, discs with different turn and fade combinations are associated with terms such as overstable, understable, stable, beginner-friendly, or wind-resistant.

### Supporting Comparative Queries

Another challenge was allowing users to compare discs using natural language. The recommendation system parses queries that reference another disc and applies numerical constraints before ranking the remaining candidates.

For example, a query such as “something faster than a Destroyer” filters the candidate discs by speed before the similarity-ranking process takes place.

### Combining Data Processing and Machine Learning

The project combines live API data, data cleaning, generated disc profiles, TF-IDF vectorization, and cosine similarity.

The recommendation process is:

1. Retrieve disc data from the Try Discs API.
2. Remove discontinued discs.
3. Filter the available brands.
4. Generate descriptive profiles for each disc.
5. Parse any comparative requirements in the user's query.
6. Convert the query and disc profiles into TF-IDF vectors.
7. Rank the candidates using cosine similarity.
8. Return the highest-ranked results.

### Building the Backend and Frontend Together

The project required connecting a Python HTTP server with a browser-based JavaScript frontend. The backend serves the application files and provides API endpoints for loading brand information and generating recommendations.

## Author

Created by [Casey Pietrusewicz](https://github.com/chpietrusewicz).

## Data Attribution

Disc data is provided by [Try Discs](https://trydiscs.com).

This project uses the Try Discs API to retrieve disc names, brands, types, flight numbers, and physical specifications.

## Data Attribution

Disc data is provided by [Try Discs](https://trydiscs.com).
