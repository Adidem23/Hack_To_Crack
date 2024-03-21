from fastapi import FastAPI, HTTPException
import pandas as pd
import itertools

app = FastAPI()

# Load data
df = pd.read_csv('./drug_to_drug.csv', low_memory=False)

def check_compatibility(drug1, drug2, df):
    drug1_matches = df[df['name'].str.lower() == drug1.lower()]
    drug2_matches = df[df['name'].str.lower() == drug2.lower()]

    if drug1_matches.empty and drug2_matches.empty:
        return f"Sorry for the inconvenience, information about both {drug1} and {drug2} is unavailable."
    elif drug1_matches.empty:
        return f"Sorry for the inconvenience, information about {drug1} is unavailable."
    elif drug2_matches.empty:
        return f"Sorry for the inconvenience, information about {drug2} is unavailable."
    
    drug1_id = drug1_matches['drugbank-id'].iloc[0]
    drug2_id = drug2_matches['drugbank-id'].iloc[0]

    incompatible_drugs_ids = df[df['drugbank-id'] == drug1_id]['drug-interactions'].iloc[0].split()

    if drug2_id in incompatible_drugs_ids:
        return f"{drug1} and {drug2} are not compatible."
    else:
        return f"{drug1} and {drug2} are compatible."

def check_compatibility_for_multiple_drugs(drug_names, df):
    drugs = [name.strip() for name in drug_names.split(',')]
    unavailable_drugs = []
    available_drugs = []
    
    # First loop: Check for unavailable drugs and remove them from the list
    for drug in drugs:
        drug_matches = df[df['name'].str.lower() == drug.lower()]
        if drug_matches.empty:
            unavailable_drugs.append(drug)
        else:
            available_drugs.append(drug)
    
    for drug in unavailable_drugs:
        print(f"Sorry for the inconvenience, information about {drug} is unavailable.")
        drugs.remove(drug)
    
    # Second loop: Check compatibility for available drugs
    result = []
    for i in range(len(available_drugs)):
        for j in range(i + 1, len(available_drugs)):
            result.append(check_compatibility(available_drugs[i], available_drugs[j], df))
    return result

@app.post("/check/{drug_names}")
async def check_compatibility_endpoint(drug_names: str):
    results = check_compatibility_for_multiple_drugs(drug_names, df)
    for res in results:
        print(res)
    return results