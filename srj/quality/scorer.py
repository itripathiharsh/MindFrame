import math

class QualityScorer:
    def __init__(self, cfg):
        self.cfg = cfg

    def score(self, faces, pose):
        """
        Calculates a Quality Score (0-100) and determines Orientation.
        Returns: (score, orientation_string)
        """
        
        # --- 1. FACE DETECTION CHECK (With Fallback) ---
        has_face_box = len(faces) > 0
        
        if not has_face_box:
            # [FIX]: Agar Face Detector fail ho jaye (jaise banda neeche dekh raha hai),
            # toh hum Pose Landmarks check karenge.
            if pose and pose["nose"]["vis"] > 0.6:
                # Naak visible hai, matlab banda present hai
                return 45, "Indistinct"
            else:
                # Na Face mila, na Pose -> Ye confirm BACK view hai
                return 0, "Back (No Face)"

        # --- 2. BASE SCORING ---
        # Agar Face Box hai, toh base score start karo
        score = 40
        confidence = faces[0]["confidence"]
        if confidence > 0.8:
            score += 10

        # --- 3. POSE GEOMETRY CHECK ---
        if not pose:
            # Face hai par body landmarks clear nahi hain
            return 50, "Face-Only"

        # Landmarks extract karo
        nose = pose["nose"]
        l_ear = pose["left_ear"]
        r_ear = pose["right_ear"]

        # A. NOSE VISIBILITY CHECK
        # Agar naak ki visibility kam hai, toh banda side/back dekh raha hai
        if nose["vis"] < 0.4:
            return 20, "Back/Obscured"

        # B. PROFILE CHECK (Ear Visibility Logic)
        # Rule: Agar ek kaan gayab hai aur dusra visible hai, toh wo Side Profile hai.
        
        # Left Ear Gayab (< 0.3) + Right Ear Visible (> 0.5) = Looking RIGHT
        if l_ear["vis"] < 0.3 and r_ear["vis"] > 0.5:
            return 45, "Profile-Right"
        
        # Right Ear Gayab (< 0.3) + Left Ear Visible (> 0.5) = Looking LEFT
        if r_ear["vis"] < 0.3 and l_ear["vis"] > 0.5:
            return 45, "Profile-Left"

        # C. FRONTAL vs SEMI-PROFILE (Ratio Logic)
        # Ab hum maan rahe hain ki Dono Kaan Visible hain (Frontal territory)
        
        dist_l = abs(nose["x"] - l_ear["x"])
        dist_r = abs(nose["x"] - r_ear["x"])
        total_w = dist_l + dist_r

        if total_w == 0:
            return 0, "Error"

        # Ratio: 0.5 means exact center.
        # < 0.5 means closer to Left Ear (Looking Left)
        # > 0.5 means closer to Right Ear (Looking Right)
        ratio = dist_l / total_w

        # --- FINAL CLASSIFICATION ---
        if 0.40 <= ratio <= 0.60:
            # Perfect Frontal (Naak beech mein hai)
            return 100, "Frontal"
        
        elif ratio < 0.40:
            # Nose Left Ear ke paas hai -> Looking Left
            if ratio < 0.25: 
                return 60, "Semi-Left"
            else:
                return 80, "Slight-Left" # Almost Frontal
            
        else: # ratio > 0.60
            # Nose Right Ear ke paas hai -> Looking Right
            if ratio > 0.75: 
                return 60, "Semi-Right"
            else:
                return 80, "Slight-Right" # Almost Frontal