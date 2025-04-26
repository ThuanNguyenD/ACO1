import streamlit as st
import streamlit.components.v1 as components
import googlemaps
import numpy as np
from ant_colony import AntColony

API_KEY = 'AIzaSyBnEczbljpLOsESpId-YPwFWQNc4YuYLEk'
gmaps = googlemaps.Client(key=API_KEY)

def get_distance_matrix(locations):
    n = len(locations)
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i][j] = np.inf
            else:
                result = gmaps.distance_matrix(origins=locations[i], destinations=locations[j], mode="driving")
                matrix[i][j] = result['rows'][0]['elements'][0]['distance']['value']
    return matrix

def extract_district(address):
    for part in address.split(','):
        if 'Quận' in part or 'quận' in part:
            return part.strip()
    return 'Unknown'

def main():
    st.title("🚛 Route Optimization by District (ACO + Google Maps)")

    raw_input = st.text_area("Enter the list of addresses (one address per line):", height=200)

    locations = [line.strip() for line in raw_input.strip().split('\n') if line.strip()]
    option = st.radio( "Do you want to classify by district",("Yes", "No"))

    district_counts = {}
    for loc in locations:
        district = extract_district(loc)
        if district != 'Không xác định':
            district_counts[district] = district_counts.get(district, 0) + 1
    
    if  option == "Yes":
        districts = sorted([district for district, count in district_counts.items() if districtscount >= 2])
        selected_district = st.selectbox("Select a district to optimize route:", districts)

        filtered_locations = [loc for loc in locations if extract_district(loc) == selected_district]
    else:
        filtered_locations = locations

        filtered_locations = [line.strip() for line in raw_input.strip().split('\n') if line.strip()]
        if len(filtered_locations) < 2:
            st.error("At least 2 locations are required!")
            return

    print(filtered_locations)

    if st.button("Optimize Route"):
        if len(locations) < 2:
            st.error("At least 2 locations are required!")
            return

        with st.spinner('Calculating...'):
            try:
                matrix = get_distance_matrix(filtered_locations)
                colony = AntColony(matrix, n_ants=10, n_best=3, n_iterations=20, decay=0.9)
                best_path = colony.run()[0]

                result = [filtered_locations[int(i)] for i, _ in best_path] + [filtered_locations[int(best_path[-1][1])]]
                st.success("Optimal Route:")
                st.write(" → ".join(result))

                # Create Google Maps Embed URL
                origin = result[0].replace(' ', '+')
                destination = result[-1].replace(' ', '+')
                waypoints = '|'.join([loc.replace(' ', '+') for loc in result[1:-1]])
                embed_url = f"https://www.google.com/maps/embed/v1/directions?key={API_KEY}&origin={origin}&destination={destination}&waypoints={waypoints}"

                components.iframe(embed_url, height=500)

            except Exception as e:
                st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
