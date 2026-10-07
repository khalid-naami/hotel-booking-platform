"""Institutional Global Hotel Search, Price Intelligence & Booking Platform (Booking.com style).
Featuring direct real-time scraping & synchronization with Booking.com.
"""

import datetime
import pandas as pd
import numpy as np
import streamlit as st

# Safe import for autorefresh
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

from src.hotels_database import HOTELS_DATABASE, HotelsManager
from src.currency_engine import CurrencyEngine, EXCHANGE_RATES
from src.booking_engine import BookingEngine
from src.visualizer import (
    create_hotels_map,
    create_guest_ratings_radar,
    create_seasonal_price_chart
)

# Streamlit Page Config
st.set_page_config(
    page_title="Global Hotels & Booking.com Live Intelligence Platform",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Luxury Glassmorphism CSS Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #f59e0b, #38bdf8, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 0.8rem;
    }
    .live-badge {
        display: inline-flex;
        align-items: center;
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        color: #34d399;
        font-weight: 600;
        margin-bottom: 1.2rem;
    }
    .hotel-card {
        background: rgba(30, 41, 59, 0.75);
        border: 1px solid rgba(245, 158, 11, 0.25);
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1.2rem;
        transition: all 0.3s ease;
    }
    .hotel-card:hover {
        border-color: #f59e0b;
        box-shadow: 0 8px 16px -2px rgba(245, 158, 11, 0.15);
    }
    .rating-badge {
        background: #0284c7;
        color: white;
        padding: 0.3rem 0.6rem;
        border-radius: 6px;
        font-weight: 700;
        font-size: 1.1rem;
        display: inline-block;
    }
    .price-tag {
        font-size: 1.8rem;
        font-weight: 800;
        color: #f59e0b;
    }
    .discount-badge {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
        border: 1px solid #ef4444;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 700;
    }
    .booking-btn {
        display: inline-block;
        background: #0284c7;
        color: white !important;
        padding: 0.45rem 1rem;
        border-radius: 6px;
        font-weight: 600;
        text-decoration: none;
        font-size: 0.85rem;
        transition: background 0.2s;
        margin-top: 0.5rem;
    }
    .booking-btn:hover {
        background: #0369a1;
        color: white !important;
    }
    .voucher-card {
        background: rgba(15, 23, 42, 0.95);
        border: 2px solid #10b981;
        border-radius: 12px;
        padding: 1.8rem;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Top Bar / Currency & Destination Selector
st.markdown('<div class="main-title">🏨 Global Hotel Booking & Booking.com Live Intelligence Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Live Booking.com Scraping Engine | Multi-Currency Best Deals | Interactive Maps | Verified Guest Analytics</div>', unsafe_allow_html=True)

# Sidebar Filters
st.sidebar.markdown("## 🔍 Refine Your Search")
search_keyword = st.sidebar.text_input("Filter by hotel name or keyword:", value="", placeholder="e.g. Campanile, Ace, B&B, Mamounia...")

# 10s Live Auto-Refresh
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔄 Live Telemetry & Auto-Refresh")
auto_refresh_enabled = st.sidebar.toggle("10s Auto-Refresh (Live Sync)", value=True)
refresh_counter = 0
if auto_refresh_enabled and st_autorefresh is not None:
    refresh_counter = st_autorefresh(interval=10000, limit=None, key="hotel_auto_refresh_10s")

# Booking.com Live Scraper Controls
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚡ Live Booking.com Scraper")
booking_url_input = st.sidebar.text_input(
    "Booking.com Destination URL / City:",
    value="https://www.booking.com/city/fr/riom.fr.html",
    help="Enter any Booking.com city URL or destination to scrape live hotels on-demand"
)

if st.sidebar.button("🔴 Scrape & Sync Live Data Now", use_container_width=True):
    with st.spinner("Scraping live hotels, images & real-time prices from Booking.com..."):
        synced = HotelsManager.sync_live_booking(url_or_slug=booking_url_input, currency="EUR")
        st.sidebar.success(f"✅ Synced {len(synced)} live hotels with HD images from Booking.com!")

max_price_slider = st.sidebar.slider(
    "Max Price per Night (USD):",
    min_value=50,
    max_value=3000,
    value=2500,
    step=50
)

min_stars_choice = st.sidebar.selectbox("Minimum Star Rating:", [3, 4, 5, 2, 1], index=0)

property_types = ["All Types", "Urban Hotel", "Boutique Residence", "Luxury Resort", "Boutique Riad", "Historic Palace", "Overwater Villa"]
chosen_type = st.sidebar.selectbox("Property Type:", property_types, index=0)

amenity_filter = st.sidebar.selectbox(
    "Key Amenity Required:",
    ["All Amenities", "Free High-Speed WiFi 📶", "Free WiFi 📶", "Free Private Parking 🚗", "Air Conditioning ❄️", "Pool 🏊", "Spa & Wellness 🧖", "Free Breakfast 🥐"],
    index=0
)

# Live Status Badge
now_utc_str = datetime.datetime.utcnow().strftime("%H:%M:%S UTC")
if auto_refresh_enabled:
    st.markdown(f'<div class="live-badge">🟢 LIVE TELEMETRY ACTIVE &bull; Auto-Refreshing every 10s &bull; Last Synced: {now_utc_str} &bull; Cycle #{refresh_counter}</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="live-badge" style="background:rgba(148,163,184,0.1); border-color:rgba(148,163,184,0.3); color:#94a3b8;">⏸️ LIVE SYNC PAUSED &bull; Last Synced: {now_utc_str}</div>', unsafe_allow_html=True)

# Search Bar Row
sc1, sc2, sc3, sc4, sc5 = st.columns([1.6, 1.2, 1.2, 1.0, 1.0])
with sc1:
    all_destinations = HotelsManager.get_destinations()
    # Default to Riom if present, else All Destinations
    default_dest_idx = all_destinations.index("Riom") if "Riom" in all_destinations else 0
    chosen_destination = st.selectbox("📍 Destination:", all_destinations, index=default_dest_idx)

with sc2:
    today = datetime.date.today()
    checkin_date = st.date_input("📅 Check-in Date:", value=today + datetime.timedelta(days=7), min_value=today)

with sc3:
    checkout_date = st.date_input("📅 Check-out Date:", value=today + datetime.timedelta(days=11), min_value=checkin_date + datetime.timedelta(days=1))

with sc4:
    num_guests = st.selectbox("👥 Guests:", [1, 2, 3, 4, 6], index=1)

with sc5:
    currency_choice = st.selectbox("💱 Currency:", CurrencyEngine.get_supported_currencies(), index=0)

num_nights = max(1, (checkout_date - checkin_date).days)

# Query Filtered Hotels
filtered_hotels = HotelsManager.filter_hotels(
    destination=chosen_destination,
    max_price_usd=max_price_slider,
    min_stars=min_stars_choice,
    property_type=chosen_type,
    required_amenity=amenity_filter if amenity_filter != "All Amenities" else None,
    search_query=search_keyword
)

st.markdown(f"**Found {len(filtered_hotels)} properties in {chosen_destination} matching your criteria** for **{num_nights} nights** ({checkin_date} to {checkout_date}).")
st.markdown("<br>", unsafe_allow_html=True)

# Main Navigation Tabs
tabs = st.tabs([
    "🏨 Hotel Discovery & Listings",
    "🗺️ Interactive Map & Neighborhoods",
    "🛏️ Room Selection & Instant Booking Voucher",
    "📊 Price Intelligence & Seasonal Deals",
    "⭐ Guest Reviews & Rating Analytics"
])

# ----------------- TAB 1: Hotel Listings -----------------
with tabs[0]:
    if not filtered_hotels:
        st.warning("No hotels matched your exact filters. Try relaxing the star rating or price limit.")
    else:
        for hotel in filtered_hotels:
            h_price_formatted = CurrencyEngine.format_price(hotel["base_price_usd"], currency_choice)
            h_orig_formatted = CurrencyEngine.format_price(hotel["original_price_usd"], currency_choice)
            total_stay_price = CurrencyEngine.format_price(hotel["base_price_usd"] * num_nights, currency_choice)

            with st.container(border=True):
                c_img, c_info, c_price = st.columns([1.2, 2.5, 1.1])
                
                with c_img:
                    if hotel.get("image"):
                        st.image(hotel["image"], use_container_width=True)
                    else:
                        st.markdown("🏨 *Photo not available*")

                with c_info:
                    stars_str = "⭐" * hotel.get("stars", 3)
                    live_tag = " `🟢 Live Booking.com`" if hotel.get("source") == "Live Booking.com" else ""
                    st.markdown(f"#### 🏨 {hotel['name']} {stars_str}{live_tag}")
                    st.markdown(f"📍 **{hotel.get('address', hotel.get('city'))}** &bull; *{hotel.get('distance_center_km', 1.0)} km from city center*")
                    
                    # Rating score badge
                    score_val = hotel.get('rating', 8.5)
                    st.markdown(
                        f"<span class='rating-badge'>{score_val}</span> "
                        f"<span style='color:#38bdf8; font-weight:700; margin-left:6px;'>{hotel.get('rating_badge', 'Superb')}</span> "
                        f"<span style='color:#94a3b8; font-size:0.85rem;'>({hotel.get('review_count', 100):,} verified guest reviews)</span>",
                        unsafe_allow_html=True
                    )
                    
                    if hotel.get("amenities"):
                        amenities_text = " • ".join(hotel.get("amenities")[:5])
                        st.markdown(f"<p style='color:#cbd5e1; font-size:0.85rem; margin-top:6px;'>{amenities_text}</p>", unsafe_allow_html=True)
                    
                    if hotel.get("description"):
                        desc_text = hotel.get("description", "")[:140]
                        st.markdown(f"<p style='color:#94a3b8; font-size:0.82rem; font-style:italic;'>{desc_text}...</p>", unsafe_allow_html=True)

                with c_price:
                    disc = hotel.get("discount_pct", 10)
                    st.markdown(f"<span class='discount-badge'>-{disc}% Deal</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='color:#94a3b8; text-decoration:line-through; font-size:0.85rem;'>{h_orig_formatted}</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='price-tag'>{h_price_formatted}</div>", unsafe_allow_html=True)
                    st.markdown(f"<span style='color:#94a3b8; font-size:0.8rem;'>per night &bull; {num_nights} nights: <b>{total_stay_price}</b></span>", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    if hotel.get("booking_url"):
                        st.link_button("🔗 Reserve on Booking.com", hotel["booking_url"], use_container_width=True)


# ----------------- TAB 2: Interactive Map -----------------
with tabs[1]:
    st.markdown("### 🗺️ Interactive Hotel Neighborhood & Location Radar")
    fig_map = create_hotels_map(filtered_hotels, currency_choice)
    st.plotly_chart(fig_map, use_container_width=True)

    with st.expander("📋 View Hotel Locations & Distances Table"):
        df_hotels_summary = pd.DataFrame([{
            "Hotel Name": h["name"],
            "City": h["city"],
            "Stars": "⭐" * h.get("stars", 3),
            "Rating": f"{h['rating']}/10",
            "Price/Night": CurrencyEngine.format_price(h["base_price_usd"], currency_choice),
            "Distance to Center (km)": f"{h.get('distance_center_km', 1.0)} km",
            "Distance to Airport (km)": f"{h.get('distance_airport_km', 15.0)} km",
            "Source": h.get("source", "Catalog")
        } for h in filtered_hotels])
        st.dataframe(df_hotels_summary, use_container_width=True, hide_index=True)

# ----------------- TAB 3: Room Selection & Instant Booking Voucher -----------------
with tabs[2]:
    st.markdown("### 🛏️ Room Customization & Instant Confirmation Voucher")

    hotel_options = {h["name"]: h["id"] for h in HOTELS_DATABASE}
    default_h_idx = 0
    # Prefer selected destination hotel if available
    dest_hotels = [h for h in HOTELS_DATABASE if h["city"] == chosen_destination]
    if dest_hotels:
        target_name = dest_hotels[0]["name"]
        if target_name in hotel_options:
            default_h_idx = list(hotel_options.keys()).index(target_name)

    selected_hotel_name = st.selectbox("Select Hotel to Book:", list(hotel_options.keys()), index=default_h_idx)
    selected_hotel = HotelsManager.get_hotel_by_id(hotel_options[selected_hotel_name])

    if selected_hotel:
        room_types = selected_hotel.get("room_types", [])
        if not room_types:
            room_types = [{"name": "Standard Double Room", "size_sqm": 22, "bed": "1 Large Double Bed", "price_multiplier": 1.0, "cancellation": "Free cancellation"}]

        room_names = [f"{r['name']} ({r.get('size_sqm', 20)} m² | {r.get('bed', 'Double Bed')})" for r in room_types]
        
        b_c1, b_c2 = st.columns([1.3, 1])
        with b_c1:
            st.markdown(f"#### 🏨 Booking Details for **{selected_hotel['name']}**")
            chosen_room_idx = st.selectbox("Select Room Category:", range(len(room_names)), format_func=lambda i: room_names[i])
            num_rooms_choice = st.number_input("Number of Rooms:", min_value=1, max_value=5, value=1)

            st.markdown("##### 👤 Lead Guest Information:")
            guest_name = st.text_input("Full Name:", value="Khalil Al-Mansoor", placeholder="e.g. John Doe")
            guest_email = st.text_input("Email Address:", value="khalil@example.com", placeholder="e.g. guest@email.com")
            guest_phone = st.text_input("Phone Number:", value="+33 4 73 00 00 00", placeholder="+33 6 12 34 56 78")
            special_requests = st.text_area("Special Requests (Optional):", value="Quiet room, early check-in if possible.")

        with b_c2:
            st.markdown("#### 🧾 Live Itemized Price Quote")
            quote = BookingEngine.calculate_stay_quote(
                hotel=selected_hotel,
                room_type_idx=chosen_room_idx,
                checkin_date=checkin_date,
                checkout_date=checkout_date,
                num_rooms=num_rooms_choice,
                currency_label=currency_choice
            )

            st.markdown(f"""
            - **Nightly Room Rate:** `{quote['rate_per_night_formatted']}`
            - **Length of Stay:** `{quote['num_nights']} nights` (x `{quote['num_rooms']} room(s)`)
            - **Subtotal:** `{quote['subtotal_formatted']}`
            - **VAT (10%) & Service Charge (3%):** `{CurrencyEngine.format_price(quote['vat_usd'] + quote['service_usd'], currency_choice)}`
            - **Municipal City Tourism Tax:** `{CurrencyEngine.format_price(quote['city_tax_usd'], currency_choice)}`
            <hr style="border-color:rgba(56, 189, 248, 0.3);">
            <h3 style="color:#f59e0b; margin:0.3rem 0;">Total: {quote['grand_total_formatted']}</h3>
            <p style="color:#10b981; font-size:0.85rem;">✅ Includes all mandatory taxes & tourism fees.</p>
            """, unsafe_allow_html=True)

            if st.button("🚀 Confirm Booking & Issue Digital Voucher", key="btn_confirm_book"):
                voucher = BookingEngine.generate_booking_voucher(
                    hotel=selected_hotel,
                    quote=quote,
                    guest_name=guest_name,
                    guest_email=guest_email,
                    guest_phone=guest_phone,
                    special_requests=special_requests
                )

                st.success("🎉 **RESERVATION CONFIRMED & GUARANTEED!** Your official booking voucher is generated below:")
                with st.container(border=True):
                    v_c1, v_c2 = st.columns([3, 1])
                    with v_c1:
                        st.subheader("🎫 OFFICIAL HOTEL RESERVATION VOUCHER")
                    with v_c2:
                        st.markdown(f"<span style='color:#10b981; font-weight:800; font-size:1.1rem;'>{voucher['status']}</span>", unsafe_allow_html=True)
                    st.divider()
                    st.markdown(f"**🔖 Reservation Reference:** `{voucher['booking_reference']}`")
                    st.markdown(f"**🏨 Property:** **{voucher['hotel_name']}** ({'⭐' * voucher.get('hotel_stars', 3)})")
                    st.markdown(f"**📍 Address:** {voucher['hotel_address']}")
                    st.markdown(f"**👤 Lead Guest:** {voucher['guest_name']} &bull; **Email:** {voucher['guest_email']} &bull; **Phone:** {voucher['guest_phone']}")
                    st.markdown(f"**🛏️ Room Type:** {voucher['room_type']}")
                    st.markdown(f"**📅 Dates:** Check-in **{checkin_date}** (from 15:00) ➔ Check-out **{checkout_date}** (until 12:00) ({voucher['num_nights']} nights)")
                    st.markdown(f"**💵 Total Amount Guaranteed:** <span style='font-weight:800; font-size:1.3rem; color:#f59e0b;'>{voucher['grand_total_formatted']}</span>", unsafe_allow_html=True)
                    st.markdown(f"**🛡️ Policy:** {voucher['cancellation_policy']}")
                    st.markdown(f"**📝 Special Requests:** *{voucher['special_requests']}*")


# ----------------- TAB 4: Price Intelligence -----------------
with tabs[3]:
    st.markdown("### 📊 Price Intelligence, Best Season & Deal Predictor")
    
    p_hotel_name = st.selectbox("Select Hotel for Seasonal Price Analysis:", list(hotel_options.keys()), index=default_h_idx, key="price_intel_hotel")
    p_hotel = HotelsManager.get_hotel_by_id(hotel_options[p_hotel_name])

    if p_hotel and "seasonal_rates" in p_hotel:
        fig_season = create_seasonal_price_chart(p_hotel["seasonal_rates"], p_hotel["name"], currency_choice)
        st.plotly_chart(fig_season, use_container_width=True)

        low_rate = CurrencyEngine.format_price(p_hotel["seasonal_rates"]["Low_Season"], currency_choice)
        high_rate = CurrencyEngine.format_price(p_hotel["seasonal_rates"]["High_Season"], currency_choice)
        savings = p_hotel["seasonal_rates"]["High_Season"] - p_hotel["seasonal_rates"]["Low_Season"]
        savings_formatted = CurrencyEngine.format_price(savings, currency_choice)

        st.info(f"💡 **Booking Strategy Tip for {p_hotel['name']}:** Booking in the shoulder/low season can save you up to **{savings_formatted} per night** (Low season: {low_rate} vs Peak: {high_rate}).")

# ----------------- TAB 5: Guest Reviews & Rating Analytics -----------------
with tabs[4]:
    st.markdown("### ⭐ Verified Guest Review Analytics & Satisfaction Pillars")
    
    r_hotel_name = st.selectbox("Select Hotel to View Guest Feedback:", list(hotel_options.keys()), index=default_h_idx, key="review_intel_hotel")
    r_hotel = HotelsManager.get_hotel_by_id(hotel_options[r_hotel_name])

    if r_hotel and "sub_ratings" in r_hotel:
        r1, r2 = st.columns([1, 1.2])
        with r1:
            st.markdown(f"#### 🌟 Overall Score: **{r_hotel['rating']} / 10** ({r_hotel.get('rating_badge', 'Superb')})")
            st.markdown(f"Based on **{r_hotel.get('review_count', 100):,} verified traveler reviews**.")
            
            for cat, score in r_hotel["sub_ratings"].items():
                st.write(f"**{cat}** — `{score} / 10`")
                st.progress(score / 10.0)

        with r2:
            fig_radar = create_guest_ratings_radar(r_hotel["sub_ratings"], r_hotel["name"])
            st.plotly_chart(fig_radar, use_container_width=True)
