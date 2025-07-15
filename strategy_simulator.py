import matplotlib.pyplot as plt
from itertools import product
import streamlit as st


def calculate_degradation(lap, base_degradation, track_temp, driver_aggression, wetness):
    alpha = 0.02  # temp sensitivity
    beta = 0.05  # aggression sensitivity
    gamma = 0.1  # wetness sensitivity
    T_ref = 30  # reference temp Celsius

    degradation_factor = (
        (lap**2)
        * (1 + alpha * (track_temp - T_ref))
        * (1 + beta * driver_aggression)
        * (1 - gamma * wetness)
    )
    degradation_factor = max(degradation_factor, 0)  # prevent negative degradation

    return base_degradation * degradation_factor


def generate_stint_lengths(total, parts, min_stint=5):
    results = []

    def backtrack(so_far, remaining, depth):
        if depth == 1:
            if remaining >= min_stint:
                results.append(so_far + [remaining])
            return
        for i in range(min_stint, remaining - min_stint * (depth - 1) + 1):
            backtrack(so_far + [i], remaining - i, depth - 1)

    backtrack([], total, parts)
    return results


def simulate_strategy(strategy, tyre_data, pit_loss, track_temp, driver_aggression, wetness, fuel_effect_per_lap=0.5):
    total_race_time = 0
    lap_times = []

    for stint_index, stint in enumerate(strategy):
        compound = stint["compound"]
        stint_length = stint["stint_length"]

        base = tyre_data[compound]["base_lap_time"]
        base_degradation = tyre_data[compound]["degradation"]

        fuel_load = stint_length

        for lap_on_tyre in range(stint_length):
            degradation = calculate_degradation(
                lap_on_tyre, base_degradation, track_temp, driver_aggression, wetness
            )

            fuel_time_penalty = fuel_load * fuel_effect_per_lap

            lap_time = base + degradation + fuel_time_penalty
            lap_times.append(lap_time)
            total_race_time += lap_time

            fuel_load -= 1

        
        if stint_index < len(strategy) - 1:
            next_compound = strategy[stint_index + 1]["compound"]
            if compound != next_compound:
                total_race_time += pit_loss

    return total_race_time, lap_times


def has_at_least_one_compound_change(stint_compounds):
    """Return True if at least one compound change happens in the stint sequence."""
    for i in range(len(stint_compounds) - 1):
        if stint_compounds[i] != stint_compounds[i + 1]:
            return True
    return False


def find_best_strategy(total_laps, tyre_data, pit_loss, track_temp, driver_aggression, wetness):
    compounds = list(tyre_data.keys())
    best_time = float("inf")
    best_strategy = None

    for num_stints in [1, 2, 3]:
        for stint_compounds in product(compounds, repeat=num_stints):
            # At least one compound change
            if num_stints > 1 and not has_at_least_one_compound_change(stint_compounds):
                continue  

            for stint_lengths in generate_stint_lengths(total_laps, num_stints, min_stint=5):
                strategy = [
                    {"compound": comp, "stint_length": length}
                    for comp, length in zip(stint_compounds, stint_lengths)
                ]

                total_time, _ = simulate_strategy(
                    strategy, tyre_data, pit_loss, track_temp, driver_aggression, wetness
                )

                if total_time < best_time:
                    best_time = total_time
                    best_strategy = strategy

    return best_time, best_strategy


def main():
    st.title("F1 Race Strategy Simulator")

    total_laps = st.number_input("Total race laps", min_value=1, max_value=100, value=30)
    track_temp = st.slider("Track temperature (°C)", min_value=0, max_value=50, value=35)
    driver_aggression = st.slider("Driver aggression (0 to 1)", min_value=0.0, max_value=1.0, value=0.8)
    wetness = st.slider("Track wetness (0 dry - 1 wet)", min_value=0.0, max_value=1.0, value=0.0)
    pit_loss = st.number_input("Pit stop time penalty (seconds)", min_value=5, max_value=60, value=20)
    fuel_effect_per_lap = st.number_input("Fuel load effect (sec per lap of fuel)", min_value=0.0, max_value=5.0, value=0.5, step=0.1)

    tyres = {
        "soft": {"base_lap_time": 90.0, "degradation": 0.3},
        "medium": {"base_lap_time": 91.5, "degradation": 0.2},
        "hard": {"base_lap_time": 93.0, "degradation": 0.1},
    }

    best_time, best_strategy = find_best_strategy(
        total_laps, tyres, pit_loss, track_temp, driver_aggression, wetness
    )

    st.subheader("Best Strategy Found:")
    for stint in best_strategy:
        st.write(f"- {stint['compound'].capitalize()} for {stint['stint_length']} laps")

    _, lap_times = simulate_strategy(
        best_strategy, tyres, pit_loss, track_temp, driver_aggression, wetness, fuel_effect_per_lap
    )
    lap_numbers = list(range(1, len(lap_times) + 1))

    st.line_chart(data={"Lap Times (s)": lap_times}, use_container_width=True)

    total = int(best_time)
    hr = total // 3600
    mins = (total % 3600) // 60
    secs = total % 60
    st.write(f"Estimated race time: {hr}h {mins}m {secs}s")


if __name__ == "__main__":
    main()
