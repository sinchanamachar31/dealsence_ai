from backend.scripts.demo_data import DEMO_CREATORS


_REEL_DETAILS = {
    "food_demo_01_ragi_bowl": {
        "hook": "a cosy breakfast that keeps mornings simple",
        "materials": "ragi flour, banana, milk, cardamom, toasted seeds",
        "steps": (
            "whisk ragi into warm milk slowly",
            "simmer until creamy, stirring all along",
            "fold banana in and scatter seeds",
        ),
        "detail": "the glossy porridge and toasted crunch",
        "tip": "start with a splash of milk, then adjust",
        "benefit": "a comforting, filling start to your morning",
        "result": "a warm ragi bowl beside a sunny breakfast table",
        "setting": "a bright, relaxed home breakfast nook",
    },
    "food_demo_02_label_reading": {
        "hook": "you want to compare pantry labels calmly",
        "materials": "two pantry jars, ingredient labels, serving sizes",
        "steps": (
            "compare serving sizes before front claims",
            "read each ingredient list from the start",
            "choose the jar that suits your kitchen",
        ),
        "detail": "the ingredient order on both labels",
        "tip": "front-of-pack claims are only a starting point",
        "benefit": "clearer choices that fit your own kitchen",
        "result": "two jars neatly compared on a kitchen counter",
        "setting": "a tidy, naturally lit kitchen counter",
    },
    "food_demo_04_dahi_protein_bowl": {
        "hook": "you need a quick savoury lunch idea",
        "materials": "dahi, cucumber, roasted chickpeas, herbs, lemon",
        "steps": (
            "spoon cool dahi into a wide bowl",
            "chop cucumber and scatter roasted chickpeas",
            "finish with herbs, lemon, and pepper",
        ),
        "detail": "creamy dahi beside crisp chickpeas",
        "tip": "keep the crunchy toppings separate until serving",
        "benefit": "a satisfying mix of freshness and crunch",
        "result": "a colourful savoury dahi bowl ready for lunch",
        "setting": "a clean lunch table with soft daylight",
    },
    "food_demo_05_cooking_oil_smoke_point": {
        "hook": "you are choosing an oil for cooking",
        "materials": "two cooking oils, labels, a pan, tasting spoons",
        "steps": (
            "check each label and intended cooking use",
            "compare flavour, smoke point, and bottle size",
            "match the oil to your usual recipes",
        ),
        "detail": "the clear labels and golden oil colours",
        "tip": "consider flavour and use, not one headline claim",
        "benefit": "more thoughtful choices for everyday cooking",
        "result": "two oils organised beside a well-used stovetop",
        "setting": "a home kitchen with warm natural light",
    },
    "food_demo_07_chana_cucumber_salad": {
        "hook": "you want a bright, speedy lunch",
        "materials": "chana, cucumber, tomato, herbs, lemon, spices",
        "steps": (
            "rinse chana and drain it well",
            "dice cucumber and tomato into small pieces",
            "toss everything with lemon and herbs",
        ),
        "detail": "juicy tomato, crisp cucumber, and glossy chana",
        "tip": "add the lemon dressing just before eating",
        "benefit": "a colourful, satisfying bowl with fresh vegetables",
        "result": "a generous chana salad served with lemon wedges",
        "setting": "a sunny kitchen table ready for lunch",
    },
    "food_demo_08_clean_pantry_oats": {
        "hook": "you are picking oats for breakfast",
        "materials": "rolled oats, two packets, a bowl, a spoon",
        "steps": (
            "turn both packets and compare ingredient lists",
            "check the texture and cooking instructions",
            "pick a type that suits your routine",
        ),
        "detail": "the difference between thick and fine flakes",
        "tip": "check serving size and storage before deciding",
        "benefit": "a pantry staple chosen to fit your mornings",
        "result": "rolled oats poured into a simple breakfast bowl",
        "setting": "a calm pantry shelf and breakfast counter",
    },
    "food_demo_10_colorful_lunchbox_prep": {
        "hook": "you are packing a colourful lunchbox",
        "materials": "lemon rice, crunchy vegetables, yoghurt dip, containers",
        "steps": (
            "portion lemon rice into the lunchbox",
            "add dry vegetables in a separate section",
            "pack yoghurt dip in a sealed cup",
        ),
        "detail": "bright vegetables beside fragrant lemon rice",
        "tip": "let warm rice cool before closing the box",
        "benefit": "an inviting lunch with practical make-ahead pieces",
        "result": "a neatly packed lunchbox ready for a busy day",
        "setting": "a bright kitchen counter during morning prep",
    },
    "beauty_demo_01_gentle_cleanser_review": {
        "hook": "you want a gentle start to skincare",
        "materials": "a mild cleanser, clean hands, water, soft towel",
        "steps": (
            "wet your face and dispense a small amount",
            "massage gently without scrubbing the skin",
            "rinse well and pat dry with a towel",
        ),
        "detail": "the cleanser's soft texture as it lathers",
        "tip": "follow the label and notice how your skin feels",
        "benefit": "a simple cleanse without adding extra steps",
        "result": "a clean sink-side routine with a soft towel",
        "setting": "a bright bathroom shelf with uncluttered products",
    },
    "beauty_demo_02_barrier_routine": {
        "hook": "your skincare routine could feel simpler",
        "materials": "gentle cleanser, plain moisturiser, daily sunscreen",
        "steps": (
            "cleanse gently and rinse with comfortable water",
            "smooth on moisturiser while skin feels comfortable",
            "finish with sunscreen as its label directs",
        ),
        "detail": "light layers settling without rubbing the skin",
        "tip": "introduce new products gradually, one at a time",
        "benefit": "a steady routine that supports everyday skin comfort",
        "result": "three simple products arranged beside the bathroom sink",
        "setting": "a quiet bathroom counter in soft morning light",
    },
    "beauty_demo_04_sunscreen_texture_test": {
        "hook": "you are comparing sunscreen textures today",
        "materials": "two labelled sunscreens, clean skin, a small mirror",
        "steps": (
            "read each label and use its stated amount",
            "spread each texture gently on separate areas",
            "wait, then compare the finish in daylight",
        ),
        "detail": "how each sunscreen spreads and settles",
        "tip": "follow the product directions for use and reapplication",
        "benefit": "a comfortable option for regular sun protection",
        "result": "both sunscreen finishes shown clearly in natural light",
        "setting": "a bright vanity near a window",
    },
    "beauty_demo_05_fragrance_label_breakdown": {
        "hook": "you are learning to read skincare labels",
        "materials": "two skincare boxes, ingredient lists, a notebook",
        "steps": (
            "turn the boxes around to find ingredients",
            "scan for fragrance terms and compare formulas",
            "note questions before choosing a product",
        ),
        "detail": "small ingredient names printed on the packaging",
        "tip": "the full formula matters more than a front label",
        "benefit": "more informed choices for your personal preferences",
        "result": "two labelled products compared side by side",
        "setting": "a neat vanity with soft, even lighting",
    },
    "beauty_demo_07_patch_test_basics": {
        "hook": "you are trying a new skincare product",
        "materials": "a new product, clean skin, its instruction label",
        "steps": (
            "read the product directions before applying anything",
            "test a small discreet area as directed",
            "watch how the area feels before wider use",
        ),
        "detail": "a small, careful application on the inner arm",
        "tip": "stop using it if discomfort or irritation appears",
        "benefit": "a more cautious way to introduce something new",
        "result": "the product set aside while you check your skin",
        "setting": "a calm vanity with clean hands and soft light",
    },
    "beauty_demo_08_moisturizer_texture_compare": {
        "hook": "you are choosing between gel and cream",
        "materials": "gel moisturiser, cream moisturiser, clean fingertips",
        "steps": (
            "place a small amount of each on skin",
            "spread both gently and notice their finish",
            "choose the texture you enjoy using",
        ),
        "detail": "the gel slip beside the cream's richer feel",
        "tip": "check how each layer sits with your usual sunscreen",
        "benefit": "a routine that feels comfortable and easy to repeat",
        "result": "two moisturiser textures compared on a clean vanity",
        "setting": "a bright bathroom counter with simple styling",
    },
    "beauty_demo_10_honest_toner_review": {
        "hook": "you are curious about hydrating toner",
        "materials": "a hydrating toner, clean hands, its ingredient label",
        "steps": (
            "read the ingredients and check the product directions",
            "pour a little into clean palms",
            "press gently onto skin if it feels comfortable",
        ),
        "detail": "the light watery texture between your fingertips",
        "tip": "a toner is optional, so keep what works for you",
        "benefit": "a comfortable extra step without routine pressure",
        "result": "a simple toner beside a calm evening skincare setup",
        "setting": "a softly lit vanity with minimal products",
    },
    "fitness_demo_01_desk_mobility_flow": {
        "hook": "your shoulders need a gentle desk break",
        "materials": "a sturdy chair, open floor space, comfortable clothes",
        "steps": (
            "sit tall and roll shoulders slowly backwards",
            "move hips gently while keeping feet grounded",
            "pause and breathe through each easy movement",
        ),
        "detail": "unhurried shoulder circles and a relaxed posture",
        "tip": "stay in a comfortable range and skip painful moves",
        "benefit": "a refreshing movement pause between long work sessions",
        "result": "a relaxed desk setup ready for the next task",
        "setting": "a home desk beside a clear patch of floor",
    },
    "fitness_demo_02_resistance_band_review": {
        "hook": "you are choosing bands for home workouts",
        "materials": "three resistance bands, storage pouch, open floor",
        "steps": (
            "inspect the band for wear before starting",
            "hold it securely and try a light pull",
            "compare grip, stretch, and storage after testing",
        ),
        "detail": "the band surface stretching evenly between hands",
        "tip": "start light and check gear before every session",
        "benefit": "a practical way to explore strength training at home",
        "result": "the bands stacked neatly beside their storage pouch",
        "setting": "a bright home workout corner with clear floor space",
    },
    "fitness_demo_03_bodyweight_strength_circuit": {
        "hook": "you want a simple strength circuit",
        "materials": "a stable chair, exercise mat, comfortable workout clothes",
        "steps": (
            "start with controlled bodyweight squats to a chair",
            "use an incline for steady push-up repetitions",
            "finish with a comfortable standing core hold",
        ),
        "detail": "steady feet and controlled movement through each rep",
        "tip": "choose a pace and variation that feel manageable",
        "benefit": "a flexible full-body session in a small space",
        "result": "the mat and chair ready for another easy round",
        "setting": "a welcoming home workout space with daylight",
    },
    "fitness_demo_05_foam_roller_review": {
        "hook": "you are exploring a foam roller",
        "materials": "a foam roller, exercise mat, comfortable workout clothes",
        "steps": (
            "sit beside the roller and place it under muscle",
            "move slowly with gentle, comfortable pressure",
            "pause briefly without rolling over joints",
        ),
        "detail": "the roller surface and controlled movement across muscle",
        "tip": "keep pressure comfortable and avoid bony areas",
        "benefit": "a calm recovery routine after a home workout",
        "result": "the roller resting beside a neatly rolled exercise mat",
        "setting": "a quiet home recovery corner with soft light",
    },
    "fitness_demo_06_dumbbell_row_form": {
        "hook": "you are practising a steady dumbbell row",
        "materials": "one dumbbell, a stable bench, nonslip shoes",
        "steps": (
            "brace one hand and hinge with a steady back",
            "pull the dumbbell toward your hip with control",
            "lower slowly and repeat on the other side",
        ),
        "detail": "the elbow travelling close beside the body",
        "tip": "choose a weight you can control through every rep",
        "benefit": "a focused strength move for a home routine",
        "result": "the dumbbell set down beside a stable bench",
        "setting": "a tidy home gym area with clear space",
    },
    "fitness_demo_08_adjustable_dumbbell_review": {
        "hook": "you are comparing adjustable home dumbbells",
        "materials": "adjustable dumbbells, selector dial, clear floor space",
        "steps": (
            "check the weight selector and locking mechanism",
            "change settings only while the dumbbell is racked",
            "test the grip before setting it down carefully",
        ),
        "detail": "the selector dial clicking securely into place",
        "tip": "follow the maker's instructions for safe adjustments",
        "benefit": "compact gear can save space in a home gym",
        "result": "adjustable dumbbells stored neatly after a quick review",
        "setting": "a small home gym corner with tidy storage",
    },
    "fitness_demo_09_ankle_mobility_drill": {
        "hook": "your ankles need a gentle warm-up",
        "materials": "a clear wall, stable shoes, a little floor space",
        "steps": (
            "stand facing the wall with one foot forward",
            "guide the knee forward while keeping heel grounded",
            "switch sides and move slowly within comfort",
        ),
        "detail": "the heel staying down as the knee travels",
        "tip": "use a comfortable range and never force the stretch",
        "benefit": "a simple mobility check before lower-body training",
        "result": "both feet planted comfortably beside the wall",
        "setting": "a calm workout area with an uncluttered wall",
    },
    "tech_demo_01_budget_desk_lamp": {
        "hook": "you want a budget-friendly study lamp",
        "materials": "a desk lamp, notebook, laptop, adjustable light settings",
        "steps": (
            "place the lamp beside your study materials",
            "test brightness and angle across the notebook",
            "adjust the light to reduce screen glare",
        ),
        "detail": "the pool of light across an open notebook",
        "tip": "choose a setting that feels comfortable for reading",
        "benefit": "a more usable desk for focused evening study",
        "result": "a neat desk with lamp, notebook, and laptop",
        "setting": "a student desk in a softly lit room",
    },
    "tech_demo_02_weekly_study_workflow": {
        "hook": "your study week feels a little scattered",
        "materials": "a calendar, deadline list, notebook, pen",
        "steps": (
            "write down deadlines before choosing study blocks",
            "break large topics into smaller focused sessions",
            "leave open time for breaks and surprises",
        ),
        "detail": "clear blocks of study time and open space",
        "tip": "keep the plan realistic, then adjust as needed",
        "benefit": "a calmer view of the week ahead",
        "result": "a practical weekly study plan beside an open notebook",
        "setting": "a student desk with a simple paper planner",
    },
    "tech_demo_04_keyboard_under_30": {
        "hook": "you need an affordable compact keyboard",
        "materials": "a compact keyboard, laptop, notebook, typing notes",
        "steps": (
            "connect the keyboard and check its layout",
            "type a short paragraph to test the feel",
            "note desk space, sound, and connection options",
        ),
        "detail": "compact keys beside a student notebook",
        "tip": "check compatibility and return terms before purchasing",
        "benefit": "a budget desk setup chosen with care",
        "result": "the keyboard neatly paired with a laptop",
        "setting": "a small student desk with warm daylight",
    },
    "tech_demo_05_focus_timer_app": {
        "hook": "you want a calmer study timer",
        "materials": "a phone, focus timer app, notebook, quiet desk",
        "steps": (
            "choose a short focus session in the app",
            "silence optional alerts before the timer starts",
            "take a small break when the session ends",
        ),
        "detail": "a simple timer beside an open study notebook",
        "tip": "adjust session length to suit your own attention",
        "benefit": "a gentle structure for getting started on work",
        "result": "the timer resting beside finished study notes",
        "setting": "a quiet desk with a phone and notebook",
    },
    "tech_demo_07_phone_stand_study_test": {
        "hook": "you need a small phone stand",
        "materials": "a folding phone stand, phone case, study desk",
        "steps": (
            "place the stand on a level desk surface",
            "set the phone in place with its case",
            "check the viewing angle and fold it away",
        ),
        "detail": "the stand holding a cased phone steadily",
        "tip": "keep the screen at a comfortable viewing height",
        "benefit": "a hands-free setup for calls or study references",
        "result": "a tidy desk with the stand folded beside the phone",
        "setting": "a compact student desk in natural daylight",
    },
    "tech_demo_08_digital_distraction_reset": {
        "hook": "your phone keeps interrupting study time",
        "materials": "a phone, laptop, focus settings, one study tab",
        "steps": (
            "silence optional notifications for a study block",
            "move distracting apps away from the home screen",
            "leave one useful tab ready on your laptop",
        ),
        "detail": "a clean screen with only essential study tools",
        "tip": "keep emergency contacts and useful alerts available",
        "benefit": "fewer interruptions while you work on one task",
        "result": "a calm screen and open notebook ready for study",
        "setting": "a student workspace with phone and laptop",
    },
    "tech_demo_10_exam_week_checklist": {
        "hook": "exam week is coming up quickly",
        "materials": "your syllabus, revision notes, calendar, water bottle",
        "steps": (
            "list topics and gather the notes you need",
            "schedule short revision blocks with breaks",
            "pack materials and protect your usual sleep time",
        ),
        "detail": "small topic checkboxes beside a clear calendar",
        "tip": "start with one manageable topic, not an all-nighter",
        "benefit": "a steadier plan for preparing across the week",
        "result": "a ready study desk with notes and a simple checklist",
        "setting": "a focused student desk with calm evening light",
    },
    "home_demo_01_brass_lamp_corner": {
        "hook": "you want a cosy reading corner",
        "materials": "a brass lamp, secondhand table, favourite plant",
        "steps": (
            "clear the table and place it near a seat",
            "position the lamp for a comfortable reading glow",
            "add your plant and route the cord neatly",
        ),
        "detail": "warm brass beside the plant's green leaves",
        "tip": "reuse a table you already own or find secondhand",
        "benefit": "a welcoming corner with less need to buy new",
        "result": "a softly lit reading chair beside a styled table",
        "setting": "a lived-in reading nook with afternoon light",
    },
    "home_demo_02_ceramic_mug_makers": {
        "hook": "you are choosing a handmade ceramic mug",
        "materials": "a ceramic mug, maker notes, glaze, handle",
        "steps": (
            "look closely at the glaze and rim",
            "hold the handle and check its comfortable fit",
            "read the maker's care instructions before use",
        ),
        "detail": "small glaze variations across the handmade surface",
        "tip": "ask the maker about care and shipping details",
        "benefit": "a thoughtful piece that supports local craft",
        "result": "the mug ready for a slow cup of tea",
        "setting": "a warm ceramics studio beside a worktable",
    },
    "home_demo_04_small_room_shelf_styling": {
        "hook": "your small shelf needs a calmer look",
        "materials": "one ceramic vase, a favourite book, small plant",
        "steps": (
            "place the book first to create a low base",
            "add the vase and vary the object heights",
            "leave open space around every piece",
        ),
        "detail": "the quiet balance of shapes and empty space",
        "tip": "edit one object out if the shelf feels crowded",
        "benefit": "a calmer room without adding more decor",
        "result": "a simple shelf styled with a book and vase",
        "setting": "a small bright room with a natural wood shelf",
    },
    "home_demo_05_refill_cleaning_review": {
        "hook": "you are considering a refill cleaning concentrate",
        "materials": "a refill concentrate, labelled bottle, clean water",
        "steps": (
            "read the dilution directions on the product",
            "measure carefully into a clean reusable bottle",
            "add water as directed and secure the sprayer",
        ),
        "detail": "the measured refill mixing clearly in the bottle",
        "tip": "keep the label visible and follow storage directions",
        "benefit": "a simple refill can reduce some packaging waste",
        "result": "a labelled reusable bottle ready for household cleaning",
        "setting": "a tidy laundry shelf with refill supplies",
    },
    "home_demo_07_linen_curtain_light": {
        "hook": "you want softer light in your room",
        "materials": "linen curtains, curtain rod, window, measuring tape",
        "steps": (
            "check the window width and curtain drop",
            "hang the panels evenly along the rod",
            "step back and see how the fabric drapes",
        ),
        "detail": "sunlight filtering softly through the linen weave",
        "tip": "measure first and choose a washable fabric you like",
        "benefit": "a gentle room refresh with a natural texture",
        "result": "linen curtains framing a softly lit window",
        "setting": "a relaxed bedroom with afternoon window light",
    },
    "home_demo_08_brass_care_basics": {
        "hook": "you want to care for brass gently",
        "materials": "a brass object, soft cloth, maker care instructions",
        "steps": (
            "check whether the brass has a coated finish",
            "dust with a clean soft cloth first",
            "test any cleaner on a hidden area",
        ),
        "detail": "the brass surface catching light without harsh polishing",
        "tip": "follow maker guidance and avoid abrasive scrubbing",
        "benefit": "careful cleaning helps preserve a favourite object",
        "result": "a brass decor piece returned to its shelf",
        "setting": "a quiet home shelf with warm natural light",
    },
    "home_demo_10_ceramic_planter_styling": {
        "hook": "you want to style a plant corner",
        "materials": "a ceramic planter, leafy plant, soil, protective tray",
        "steps": (
            "check the planter has suitable drainage",
            "settle the plant and soil without packing tightly",
            "place the pot on a protective tray",
        ),
        "detail": "the ceramic glaze beside fresh green leaves",
        "tip": "choose a plant and pot suited to your light",
        "benefit": "a living corner that brings warmth to a room",
        "result": "a leafy plant styled in a handmade ceramic pot",
        "setting": "a bright room corner with a wooden side table",
    },
}


def build_reel_storyboard(creator: dict, content: dict) -> dict:
    details = _REEL_DETAILS.get(content["content_slug"])
    if details is None:
        raise ValueError(
            f"No reel storyboard details for {content['content_slug']}."
        )

    step1, step2, step3 = details["steps"]
    script = (
        f"Hey guys, {details['hook']}. We need {details['materials']}. "
        f"First, {step1}. Next, {step2}. Finish with {step3}. "
        f"This helps {details['benefit']}. "
        "Thanks for being here... see you soon."
    )
    optional_phrases = (
        f"Look closely at {details['detail']}.",
        f"Remember, {details['tip']}.",
    )
    for phrase in optional_phrases:
        if len((script + " " + phrase).split()) <= 78:
            script = f"{script} {phrase}"

    padding_phrases = (
        "Take your time, and enjoy each small step.",
        "Keep it simple and make this idea your own.",
        "I hope this feels easy to try at home.",
    )
    while len(script.split()) < 68:
        available_phrases = [
            phrase
            for phrase in padding_phrases
            if len((script + " " + phrase).split()) <= 78
        ]
        if not available_phrases:
            raise ValueError(
                f"Unable to bring storyboard script for {content['content_slug']} "
                "within the requested word range."
            )
        phrase = min(
            available_phrases,
            key=lambda item: len((script + " " + item).split()),
        )
        script = f"{script} {phrase}"

    word_count = len(script.split())
    if not 68 <= word_count <= 78:
        raise ValueError(
            f"Storyboard script for {content['content_slug']} has "
            f"{word_count} words; expected 68 to 78."
        )

    caption = content["caption"]
    visual_context = (
        f"{creator['handle']} in the {creator['niche']} niche, inspired by "
        f"this reel: {caption}"
    )
    visual_style = "Natural light, realistic detail, no text overlay."
    scenes = [
        (
            f"Vertical 9:16, 5-second opening shot for {visual_context}. "
            f"Show {details['materials']} arranged clearly at {details['setting']}. "
            f"{visual_style}"
        ),
        (
            f"Vertical 9:16, 5-second preparation shot: hands begin to "
            f"{step1}, with the ingredients or tools visible. "
            f"{visual_style}"
        ),
        (
            f"Vertical 9:16, 5-second action shot: show the next action, "
            f"{step2}, from a close side angle. "
            f"{visual_style}"
        ),
        (
            f"Vertical 9:16, 5-second macro close-up of {details['detail']}; "
            f"capture the surface, movement, or small practical detail. "
            f"{visual_style}"
        ),
        (
            f"Vertical 9:16, 5-second finishing shot: {step3}, then reveal "
            f"the completed step in {details['setting']}. {visual_style}"
        ),
        (
            f"Vertical 9:16, 5-second lifestyle hero shot of {details['result']}. "
            f"Show the finished result naturally in {details['setting']}. "
            f"{visual_style}"
        ),
    ]

    return {"script": script, "scenes": scenes}


REEL_STORYBOARDS = [
    {
        "creator_handle": creator["handle"],
        "content_slug": content["content_slug"],
        **build_reel_storyboard(creator, content),
    }
    for creator in DEMO_CREATORS
    for content in creator["contents"]
    if content.get("video_path") is not None
]
