from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Contact, Farmer, Recommendation
import datetime

# ─────────────────────────────────────────────
# CROP SCHEDULE (Day-based Activity Alerts)
# ─────────────────────────────────────────────
CROP_SCHEDULE = {
    "Rice": {
        5:  ("💧", "First light irrigation", "Water the field lightly after transplanting."),
        10: ("🌿", "Apply Nitrogen fertilizer (Urea)", "Add 25 kg/acre of urea to boost early growth."),
        20: ("🐛", "First pest inspection", "Check for stem borer and apply neem spray if needed."),
        30: ("💧", "Second irrigation", "Ensure standing water of 5 cm in the field."),
        45: ("🧪", "Apply phosphorus (DAP)", "Add DAP fertilizer to strengthen root system."),
        60: ("🐛", "Spray pest control (BPH)", "Apply insecticide against Brown Plant Hopper."),
        75: ("💧", "Third irrigation", "Maintain water level carefully before flowering."),
        90: ("🌸", "Flowering stage — do not disturb", "Avoid spraying chemicals during this phase."),
        105:("🧪", "Apply potash (MOP)", "Add 20 kg/acre potash to improve grain quality."),
        115:("🌾", "Drain field for harvest", "Stop irrigation and allow field to dry for 10 days."),
        120:("🚜", "Harvest time!", "Crop is ready. Arrange harvester and storage."),
    },
    "Wheat": {
        7:  ("💧", "First irrigation (Crown Root)", "Critical irrigation at Crown Root Initiation stage."),
        15: ("🌿", "Apply Urea top dressing", "Broadcast 40 kg/acre urea after first irrigation."),
        25: ("🐛", "Weed control", "Apply herbicide to control broad-leaf weeds."),
        40: ("💧", "Second irrigation (Tillering)", "Water at tillering stage for better yield."),
        55: ("💧", "Third irrigation (Jointing)", "Provide irrigation at jointing stage."),
        70: ("🧪", "Apply foliar spray (Zinc)", "Zinc spray improves grain filling."),
        85: ("💧", "Fourth irrigation (Flowering)", "Very important irrigation before flowering."),
        100:("🌸", "Flowering — monitor for rust", "Watch for yellow rust and apply fungicide if spotted."),
        110:("💧", "Fifth irrigation (Grain filling)", "Last irrigation for grain development."),
        120:("🌾", "Prepare for harvest", "Allow crop to dry, check moisture content."),
    },
    "Maize": {
        5:  ("💧", "First irrigation", "Water gently to ensure seed germination."),
        15: ("🌿", "Apply starter fertilizer", "Add NPK 10:26:26 at 25 kg/acre."),
        25: ("🐛", "Check for Fall Army Worm", "Inspect whorl and apply chlorpyrifos if infected."),
        35: ("🌿", "Apply Urea (side dressing)", "Apply 30 kg/acre urea near plant base."),
        50: ("💧", "Critical irrigation (Tasseling)", "Do not miss this irrigation — affects yield."),
        60: ("🌸", "Pollination stage", "Avoid disturbing plants; do not spray pesticides."),
        75: ("🧪", "Apply potash", "Add 15 kg/acre MOP for grain hardening."),
        90: ("🌾", "Check grain moisture", "Harvest when moisture drops below 25%."),
    },
    "Cotton": {
        10: ("💧", "First irrigation", "Light irrigation to help seedlings establish."),
        20: ("🌿", "Apply DAP fertilizer", "50 kg/acre DAP for early root development."),
        30: ("🐛", "Aphid/Jassid inspection", "Spray imidacloprid if pest population is high."),
        45: ("💧", "Irrigation at squaring", "Water when squares (flower buds) appear."),
        55: ("🌿", "Apply Urea split dose", "Second split of nitrogen for boll development."),
        70: ("🐛", "Bollworm control", "Apply spinosad or emamectin benzoate spray."),
        90: ("💧", "Irrigation at boll opening", "Maintain moisture for uniform boll opening."),
        110:("🧪", "Defoliation (optional)", "Use defoliant for easier picking."),
        130:("🚜", "First picking", "Pick mature, open bolls to maintain quality."),
        160:("🚜", "Second/Final picking", "Complete harvest and prepare field for next crop."),
    },
    "Sugarcane": {
        15: ("💧", "First irrigation", "Water to help ratoons or planted cane establish."),
        30: ("🌿", "Apply Nitrogen (Urea)", "60 kg/acre urea as basal dose."),
        60: ("🐛", "Pyrilla pest inspection", "Check for pyrilla and apply appropriate spray."),
        90: ("🌿", "Second Nitrogen dose", "Apply 40 kg/acre urea for cane elongation."),
        120:("💧", "Irrigation — peak growth", "Ensure adequate moisture during grand growth phase."),
        180:("🧪", "Apply potash + micronutrients", "For sugar content improvement."),
        270:("🐛", "Top borer control", "Apply carbofuran granules if borer attack found."),
        330:("🌾", "Prepare for harvest", "Stop irrigation 4 weeks before cutting."),
        365:("🚜", "Harvest!", "Cut at ground level. Ratoon crop will follow."),
    },
    "Potato": {
        10: ("💧", "First irrigation", "Light sprinkle irrigation after planting."),
        20: ("🌿", "Earthing up + Urea", "Mound soil around plants, apply 20 kg/acre urea."),
        30: ("🐛", "Late blight monitoring", "Watch for brown patches, apply mancozeb spray."),
        40: ("💧", "Irrigation at stolon stage", "Critical moisture for tuber initiation."),
        55: ("🧪", "Foliar spray (Boron + Zinc)", "Improves tuber size and skin quality."),
        70: ("💧", "Irrigation at tuber bulking", "Most important for final yield."),
        80: ("🐛", "Final pest check", "Check for aphids that spread virus."),
        90: ("🌾", "Haulm killing / desiccation", "Stop irrigation and cut foliage."),
        100:("🚜", "Harvest!", "Dig carefully to avoid tuber damage."),
    },
    "Tomato": {
        7:  ("💧", "First irrigation", "Water transplants gently to establish roots."),
        15: ("🌿", "Apply starter fertilizer", "NPK 19:19:19 at 5g/litre foliar spray."),
        25: ("🐛", "Whitefly/Thrips control", "Spray imidacloprid + neem oil mixture."),
        35: ("🌸", "Flower set — apply calcium", "Calcium nitrate spray prevents blossom-end rot."),
        45: ("💧", "Drip irrigation (consistent)", "Maintain steady moisture to prevent cracking."),
        55: ("🧪", "Apply potassium sulfate", "For fruit firmness and colour."),
        65: ("🐛", "Fruit borer control", "Apply spinosad or biological Bt spray."),
        75: ("🚜", "First harvest", "Pick at 80% colour development for market."),
        90: ("🚜", "Continue picking every 5-7 days", "Regular picking improves total yield."),
    },
}

CROP_DURATIONS = {
    "Rice": 125, "Wheat": 125, "Maize": 95, "Cotton": 165,
    "Sugarcane": 365, "Potato": 105, "Tomato": 95
}

def get_crop_alerts(crop_name, start_date):
    today = datetime.date.today()
    if isinstance(start_date, datetime.datetime):
        start = start_date.date()
    else:
        start = start_date

    days_elapsed = (today - start).days
    duration = CROP_DURATIONS.get(crop_name, 120)
    schedule = CROP_SCHEDULE.get(crop_name, {})

    tasks = []
    today_task = None
    for day, (icon, title, detail) in sorted(schedule.items()):
        if days_elapsed > day + 2:
            status = "done"
        elif abs(days_elapsed - day) <= 2:
            status = "today"
            today_task = {"icon": icon, "title": title, "detail": detail, "day": day}
        else:
            status = "upcoming"
        tasks.append({
            "day": day,
            "icon": icon,
            "title": title,
            "detail": detail,
            "status": status
        })

    progress = min(100, round((days_elapsed / duration) * 100))
    days_remaining = max(0, duration - days_elapsed)

    return {
        "days_elapsed": days_elapsed,
        "duration": duration,
        "progress": progress,
        "days_remaining": days_remaining,
        "tasks": tasks,
        "today_task": today_task
    }


def get_recommendation_logic(temp, rainfall, ph, skill='beginner', farming='any'):
    crops_pool = [
        {"name": "Rice",      "temp": (20,35), "rainfall": (150,300), "ph": (5.0,7.0), "season": "Kharif",      "yield": "2.5-4.0", "profit": "₹35,000 - ₹50,000",   "risk": "Low",    "rotation": "Legumes / Pulses",  "price": "₹1,900/quintal", "icon": "🌾", "organic": "Use Neem Cake & Azolla",        "demand": "High"},
        {"name": "Wheat",     "temp": (15,25), "rainfall": (40,100),  "ph": (6.0,7.5), "season": "Rabi",        "yield": "3.0-5.0", "profit": "₹40,000 - ₹60,000",   "risk": "Medium", "rotation": "Maize / Cotton",    "price": "₹2,015/quintal", "icon": "🍞", "organic": "Vermicompost & FYM",            "demand": "Stable"},
        {"name": "Maize",     "temp": (18,30), "rainfall": (50,100),  "ph": (5.5,7.5), "season": "Kharif",      "yield": "2.0-3.5", "profit": "₹25,000 - ₹35,000",   "risk": "Low",    "rotation": "Wheat / Barley",    "price": "₹1,870/quintal", "icon": "🌽", "organic": "Green Manuring",                "demand": "Moderate"},
        {"name": "Cotton",    "temp": (22,32), "rainfall": (60,120),  "ph": (5.5,8.5), "season": "Kharif",      "yield": "1.5-2.5", "profit": "₹60,000 - ₹90,000",   "risk": "High",   "rotation": "Soybean / Maize",   "price": "₹6,025/quintal", "icon": "👕", "organic": "Bird Perches & Pheromones",     "demand": "Very High"},
        {"name": "Sugarcane", "temp": (25,35), "rainfall": (150,250), "ph": (5.0,8.5), "season": "Annual",      "yield": "60-80",   "profit": "₹80,000 - ₹1,20,000", "risk": "Medium", "rotation": "Wheat / Legumes",   "price": "₹2,850/ton",     "icon": "🍭", "organic": "Trash Mulching",                "demand": "Stable"},
        {"name": "Potato",    "temp": (15,20), "rainfall": (40,80),   "ph": (5.0,6.5), "season": "Rabi",        "yield": "15-25",   "profit": "₹45,000 - ₹70,000",   "risk": "Medium", "rotation": "Cereal Crops",      "price": "₹1,200/quintal", "icon": "🥔", "organic": "Panchagavya spray",             "demand": "Seasonal High"},
        {"name": "Tomato",    "temp": (20,28), "rainfall": (60,100),  "ph": (6.0,7.0), "season": "Year-round",  "yield": "10-15",   "profit": "₹50,000 - ₹85,000",   "risk": "High",   "rotation": "Onions / Beans",    "price": "₹2,500/quintal", "icon": "🍅", "organic": "Trichoderma viride",            "demand": "Fluctuating"},
    ]

    results = []
    for crop in crops_pool:
        if skill == 'beginner' and crop['risk'] == 'High':
            continue
        score = 0
        if crop["temp"][0] <= temp <= crop["temp"][1]:       score += 30
        else: score += max(0, 30 - abs(temp - sum(crop["temp"])/2))
        if crop["rainfall"][0] <= rainfall <= crop["rainfall"][1]: score += 30
        else: score += max(0, 30 - abs(rainfall - sum(crop["rainfall"])/2) * 0.5)
        if crop["ph"][0] <= ph <= crop["ph"][1]:             score += 40
        else: score += max(0, 40 - abs(ph - sum(crop["ph"])/2) * 5)
        if farming == 'organic': score *= 1.1
        suitability = round(min(100, score), 1)
        if suitability > 40:
            results.append({
                "name": crop["name"], "score": suitability, "yield": crop["yield"],
                "profit": crop["profit"], "risk": crop["risk"], "rotation": crop["rotation"],
                "price": crop["price"], "icon": crop["icon"], "organic_tips": crop["organic"],
                "demand_status": crop["demand"],
                "desc": f"Perfect for {skill} farmers with {ph} pH soil.",
                "soil_alert": "Warning: Avoid repeating this crop if planted last season!" if ph < 5.5 else "Soil health looks stable."
            })
    return sorted(results, key=lambda x: x['score'], reverse=True)[:5]


# ─────────────────────────────────────────────
# CORE ROUTES
# ─────────────────────────────────────────────
def home(request):
    return render(request, 'index.html')

def calendar(request):
    return render(request, 'calendar.html')

def schemes(request):
    return render(request, 'schemes.html')

def news(request):
    return render(request, 'news.html')

def about(request):
    return render(request, 'about.html')

def help_page(request):
    return render(request, 'help.html')


# ─────────────────────────────────────────────
# AUTH ROUTES
# ─────────────────────────────────────────────
def signup_view(request):
    if request.method == 'POST':
        name     = request.POST.get('name')
        email    = request.POST.get('email')
        password = request.POST.get('password')
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already exists!")
            return redirect('signup')
        user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
        messages.success(request, "Account created! Please login.")
        return redirect('login')
    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        email    = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            request.session['user_name'] = user.first_name or user.username
            messages.success(request, f"Welcome back, {request.session['user_name']}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid email or password!")
            return redirect('login')
    return render(request, 'login.html')

def logout_view(request):
    auth_logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


# ─────────────────────────────────────────────
# RECOMMENDATION ROUTES
# ─────────────────────────────────────────────
@login_required(login_url='login')
def recommend(request):
    return render(request, 'recommend.html')

@login_required(login_url='login')
def predict(request):
    if request.method == 'POST':
        try:
            temp     = float(request.POST.get('temperature', 25))
            rainfall = float(request.POST.get('rainfall', 100))
            ph       = float(request.POST.get('ph', 6.5))
            skill    = request.POST.get('skill_level', 'beginner')
            farming  = request.POST.get('farming_type', 'any')
            results  = get_recommendation_logic(temp, rainfall, ph, skill, farming)
            inputs   = {"temperature": temp, "rainfall": rainfall, "ph": ph, "plot": request.POST.get('plot_id', 'Main Field')}
            
            Recommendation.objects.create(
                user=request.user,
                temperature=temp,
                rainfall=rainfall,
                ph=ph,
                plot=inputs['plot'],
                results=results
            )
            return render(request, 'result.html', {'results': results, 'inputs': inputs})
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('recommend')
    return redirect('recommend')


# ─────────────────────────────────────────────
# CONTACT ROUTE
# ─────────────────────────────────────────────
def contact(request):
    if request.method == 'POST':
        name    = request.POST.get('name')
        email   = request.POST.get('email')
        message = request.POST.get('message')
        Contact.objects.create(name=name, email=email, message=message)
        messages.success(request, "Message sent successfully!")
        return redirect('contact')
    return render(request, 'contact.html')


# ─────────────────────────────────────────────
# USER HISTORY DASHBOARD
# ─────────────────────────────────────────────
@login_required(login_url='login')
def dashboard(request):
    user_history = Recommendation.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'dashboard.html', {'history': user_history})


# ─────────────────────────────────────────────
# FARMER REGISTRATION MODULE
# ─────────────────────────────────────────────
def register_farmer(request):
    if request.method == 'POST':
        crop_name  = request.POST.get('crop')
        duration   = int(request.POST.get('duration', CROP_DURATIONS.get(crop_name, 120)))
        start_date_str = request.POST.get('start_date')

        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except:
            start_date = datetime.date.today()

        farmer = Farmer.objects.create(
            name=request.POST.get('name'),
            village=request.POST.get('village'),
            contact=request.POST.get('contact'),
            farm_type=request.POST.get('farm_type'),
            acres=float(request.POST.get('acres', 1)),
            crop=crop_name,
            duration=duration,
            seed_quantity=request.POST.get('seed_quantity'),
            start_date=start_date,
            user=request.user if request.user.is_authenticated else None
        )
        messages.success(request, "Farm registered successfully!")
        return redirect('farmer_dashboard', farmer_id=farmer.id)

    return render(request, 'register_farmer.html', {'crop_durations': CROP_DURATIONS})


def farmer_dashboard(request, farmer_id):
    farmer = get_object_or_404(Farmer, id=farmer_id)
    alert_data = get_crop_alerts(farmer.crop, farmer.start_date)
    return render(request, 'farmer_dashboard.html', {'farmer': farmer, 'alert': alert_data})


def update_farmer(request, farmer_id):
    farmer = get_object_or_404(Farmer, id=farmer_id)

    if request.method == 'POST':
        crop_name  = request.POST.get('crop')
        duration   = int(request.POST.get('duration', CROP_DURATIONS.get(crop_name, 120)))
        start_date_str = request.POST.get('start_date')
        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except:
            start_date = farmer.start_date

        farmer.name = request.POST.get('name')
        farmer.village = request.POST.get('village')
        farmer.contact = request.POST.get('contact')
        farmer.farm_type = request.POST.get('farm_type')
        farmer.acres = float(request.POST.get('acres', 1))
        farmer.crop = crop_name
        farmer.duration = duration
        farmer.seed_quantity = request.POST.get('seed_quantity')
        farmer.start_date = start_date
        farmer.save()
        
        messages.success(request, "Farm details updated successfully!")
        return redirect('farmer_dashboard', farmer_id=farmer.id)

    return render(request, 'register_farmer.html', {'farmer': farmer, 'crop_durations': CROP_DURATIONS, 'edit_mode': True})


# ─────────────────────────────────────────────
# PUBLIC MARKETPLACE
# ─────────────────────────────────────────────
def marketplace(request):
    crop_filter = request.GET.get('crop', '')
    if crop_filter:
        all_farmers = Farmer.objects.filter(crop=crop_filter).order_by('-created_at')
    else:
        all_farmers = Farmer.objects.all().order_by('-created_at')

    farmers_list = []
    # Add expected yield to each farmer
    for f in all_farmers:
        crop_info = next((c for c in [
            {"name": "Rice", "yield": "2.5-4.0"}, {"name": "Wheat", "yield": "3.0-5.0"},
            {"name": "Maize", "yield": "2.0-3.5"}, {"name": "Cotton", "yield": "1.5-2.5"},
            {"name": "Sugarcane", "yield": "60-80"}, {"name": "Potato", "yield": "15-25"},
            {"name": "Tomato", "yield": "10-15"}
        ] if c['name'] == f.crop), None)
        
        # Django templates cannot easily assign to objects in loop like dicts unless we pass a list of dicts
        # or add a property. We'll convert to dict.
        f_dict = {
            'id': f.id,
            'name': f.name,
            'village': f.village,
            'contact': f.contact,
            'farm_type': f.farm_type,
            'acres': f.acres,
            'crop': f.crop,
            'expected_yield': crop_info['yield'] if crop_info else 'N/A',
            'seed_quantity': f.seed_quantity
        }
        farmers_list.append(f_dict)

    return render(request, 'marketplace.html', {
        'farmers': farmers_list, 
        'crop_filter': crop_filter,
        'crop_list': list(CROP_DURATIONS.keys())
    })
