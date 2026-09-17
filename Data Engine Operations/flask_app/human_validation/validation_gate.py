# ذاكرة مؤقتة للجلسات المعلقة في انتظار تأكيد المستخدم
PENDING_OPERATIONS = {}

def create_pending_action(user_session_id: str, action_type: str, target_id: str, payload: dict = None):
    """تسجيل عملية معلقة في انتظار التأكيد البشري الصريح"""
    PENDING_OPERATIONS[user_session_id] = {
        "action": action_type,    # 'DELETE' أو 'UPDATE'
        "target_id": target_id,
        "payload": payload or {}
    }

def get_pending_action(user_session_id: str):
    """جلب العملية المعلقة للمستخدم"""
    return PENDING_OPERATIONS.get(user_session_id)

def clear_pending_action(user_session_id: str):
    """مسح العملية المعلقة بعد التنفيذ أو الإلغاء"""
    if user_session_id in PENDING_OPERATIONS:
        del PENDING_OPERATIONS[user_session_id]

def is_confirmation(user_message: str) -> bool:
    """التحقق مما إذا كانت إجابة المستخدم تعبر عن الموافقة/التأكيد"""
    confirm_words = ["نعم", "تأكيد", "موافق", "احذف", "عدل", "yes", "confirm", "y", "ok"]
    return user_message.strip().lower() in confirm_words


def is_cancellation(user_message: str) -> bool:
    """التحقق مما إذا كانت إجابة المستخدم تعبر عن الإلغاء/الرفض"""
    cancel_words = ["لا", "إلغاء", "تراجع", "ارفع", "no", "cancel", "n", "stop"]
    return user_message.strip().lower() in cancel_words