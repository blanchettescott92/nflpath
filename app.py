import streamlit as st
import csv
import random
import os
import time

st.set_page_config(page_title="NFL Career Trivia", page_icon="🏈")

# --- DATA LOADING ---
@st.cache_data
def load_players(file_path):
    players = []
    if not os.path.exists(file_path):
        return []
    with open(file_path, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        reader.fieldnames = [field.strip() for field in reader.fieldnames]
        for row in reader:
            players.append({k.strip(): v.strip() for k, v in row.items() if k is not None})
    return players

# --- SESSION STATE ---
if 'all_players' not in st.session_state:
    data = load_players('nfl_players.csv')
    st.session_state.all_players = data
    indices = list(range(len(data)))
    random.shuffle(indices)
    st.session_state.remaining_indices = indices
    st.session_state.score = 0
    st.session_state.game_over = False

def next_turn():
    if len(st.session_state.remaining_indices) > 1:
        st.session_state.remaining_indices.pop(0)
    else:
        st.session_state.remaining_indices = []
        st.session_state.game_over = True

# --- APP UI ---
st.title("🏈 NFL Career Path Trivia")

if not st.session_state.game_over and st.session_state.remaining_indices:
    current_idx = st.session_state.remaining_indices[0]
    player = st.session_state.all_players[current_idx]
    
    total = len(st.session_state.all_players)
    current_num = total - len(st.session_state.remaining_indices) + 1
    
    st.write(f"Score: **{st.session_state.score}** | Progress: **{current_num}/{total}**")
    
    # Player Clues
    st.info(f"**POSITION:** {player.get('Position', 'N/A')}")
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**College:** {player.get('College', 'N/A')}")
        st.write(f"**Years:** {player.get('Playing Years', 'N/A')}")
    with c2:
        st.write(f"**Path:** {player.get('Path', 'N/A')}")

    # --- THE SEARCH-AS-YOU-TYPE BOX ---
    # We use a selectbox but we style it to feel like a search bar.
    # We only include names that match what the user is thinking.
    all_names = sorted([p['Name'] for p in st.session_state.all_players])
    
    # This component is the best balance for mobile/desktop:
    # It allows typing and filters the list as you go.
    guess = st.selectbox(
        "Search for a player name:",
        options=[""] + all_names,
        index=0,
        help="Type to search...",
        key=f"sb_{current_idx}"
    )

    # --- BUTTONS ---
    col_sub, col_skip, col_hint = st.columns(3)
    
    with col_sub:
        if st.button("Submit Guess", type="primary"):
            if guess == player['Name']:
                st.success(f"✅ Correct! It's {player['Name']}")
                st.session_state.score += 1
                time.sleep(1.5)
                next_turn()
                st.rerun()
            elif guess == "":
                st.warning("Please select a name first!")
            else:
                st.error(f"❌ Wrong! The answer was {player['Name']}")
                time.sleep(1.5)
                next_turn()
                st.rerun()

    with col_skip:
        if st.button("Skip Player ⏭️"):
            st.warning(f"Skipped! The answer was {player['Name']}")
            time.sleep(1.5)
            next_turn()
            st.rerun()

    with col_hint:
        if st.button("Pro Bowl Hint 💡"):
            st.write(f"Pro Bowls: {player.get('Pro Bowl Years', 'None listed')}")

else:
    st.balloons()
    st.header("🏆 Challenge Complete!")
    st.write(f"Final Score: {st.session_state.score} / {len(st.session_state.all_players)}")
    if st.button("Restart Game"):
        del st.session_state.all_players
        st.rerun()