# Simple referral system: All approved users receive the same access level.
approved_referrals = {"KINGFISK123", "REF456ABC", "REF789DEF"}

def is_valid_referral(referral_code: str) -> bool:
    return referral_code in approved_referrals