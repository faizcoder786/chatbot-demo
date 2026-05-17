from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from datetime import datetime
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def home():
    return FileResponse("static/chat.html")

# ====================================
# WOOCOMMERCE API
# ====================================

WC_URL = "https://mybooksfactory.com"

WC_KEY = "ck_726c8c7acd791471b911f6f70699a969a81b51d4"

WC_SECRET = "cs_ad0b799f617115ba39db0b91d102c2b99bedcc52"

# ====================================
# CORS
# ====================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====================================
# REQUEST MODEL
# ====================================

class ChatRequest(BaseModel):
    message: str
    mode: str = ""

# ====================================
# GET SINGLE ORDER
# ====================================

def get_order(order_id):

    url = f"{WC_URL}/wp-json/wc/v3/orders/{order_id}"

    response = requests.get(

        url,

        auth=(WC_KEY, WC_SECRET)

    )

    return response.json()

# ====================================
# CHAT API
# ====================================

@app.post("/chat")
async def chat(data: ChatRequest):

    msg = data.message.lower()

    mode = data.mode

    # ====================================
    # ORDER STATUS
    # ====================================

    if msg == "order_status":

        return {
            "reply": "Please enter your order ID"
        }

    # ====================================
    # TRACK SHIPMENT
    # ====================================

    elif msg == "track_shipment":

        return {
            "reply": "Please enter your order ID"
        }

    # ====================================
    # CONTACT SUPPORT
    # ====================================

    elif msg == "contact_support":

        return {
            "reply": """
📞 Call Support:
+91 2345659858

💬 WhatsApp:
https://wa.me/912345659858
"""
        }

    # ====================================
    # CANCEL ORDER
    # ====================================

    elif msg == "cancel_order":

        return {
            "reply": "Please enter your order ID for cancellation request"
        }

    # ====================================
    # REAL ORDER CHECK
    # ====================================

    elif msg.isdigit():

        order = get_order(msg)

        # ORDER NOT FOUND

        if order.get("code"):

            return {
                "reply": "Order not found ❌"
            }

        status = order["status"]

        # ====================================
        # PROCESSING
        # ====================================

        if status == "processing":

            # CANCEL ORDER FLOW

            if mode == "cancel_order":

                created_date = order["date_created"]

                order_time = datetime.strptime(
                    created_date,
                    "%Y-%m-%dT%H:%M:%S"
                )

                now = datetime.now()

                hours_passed = (now - order_time).total_seconds() / 3600

                if hours_passed >= 72:

                    return {
                        "reply": """
        Your order is eligible for cancellation.

        You will receive a FULL refund.

        Please contact support team for refund process.

        📞 +91 2345659858
        """
                    }

                # LESS THAN 3 DAYS

                else:

                    return {
                        "reply": """
        Your order is eligible for cancellation.

        Please note:
        3% cancellation charges may apply.

        Please contact support team for refund process.

        📞 +91 2345659858
        """
                    }

            # NORMAL ORDER STATUS FLOW

            return {
                "reply": """
        Your order is currently processing 😊

        Please give us some time.
        Your order will be shipped soon.
        """
            }

        # ====================================
        # COMPLETED / SHIPPED
        # ====================================

        elif status == "completed":

            tracking_number = "Not Available"

            courier = "Not Available"

            tracking_link = ""

            # META DATA LOOP

            for meta in order["meta_data"]:

                value = meta.get("value", "")

                # TRACKING DATA

                if isinstance(value, list):

                    for item in value:

                        provider = str(
                            item.get("tracking_provider", "")
                        ).lower()

                        tracking_number = item.get(
                            "tracking_number",
                            ""
                        )

                        # INDIA POST

                        if "india-post" in provider:

                            courier = "India Post"

                            tracking_link = "https://www.indiapost.gov.in"

                        # AMAZON

                        elif "amazon" in provider:

                            courier = "Amazon Shipping"

                            tracking_link = "https://track.amazon.in"

            # CANCEL ORDER FLOW

            if mode == "cancel_order":

                return {
                    "reply": """
Sorry, this order has already been shipped.

Cancellation is no longer possible.
"""
                }

            # NORMAL SHIPMENT FLOW

            return {
                "reply": f"""
Your order has been shipped.

Courier: {courier}

Consignment Number:
{tracking_number}

Track Package:
{tracking_link}
"""
            }

        # ====================================
        # FAILED PAYMENT
        # ====================================

        elif status == "failed":

            return {
                "reply": """
Your payment was unsuccessful.

If amount was deducted,
it will be refunded automatically within 5-7 working days.

Please try placing the order again.
"""
            }

        # ====================================
        # CANCELLED
        # ====================================

        elif status == "cancelled":

            return {
                "reply": """
This order has already been cancelled.
"""
            }

        # ====================================
        # REFUNDED
        # ====================================

        elif status == "refunded":

            return {
                "reply": """
Your order has already been refunded.

Please check your bank statement 😊
"""
            }

        # ====================================
        # OTHER STATUS
        # ====================================

        else:

            return {
                "reply": f"Order status: {status}"
            }

    # ====================================
    # DEFAULT
    # ====================================

    else:

        return {
            "reply": "Please select a valid option."
        }

# ====================================
# TEST ALL ORDERS
# ====================================

@app.get("/test-order")
def test_order():

    url = f"{WC_URL}/wp-json/wc/v3/orders"

    response = requests.get(

        url,

        auth=(WC_KEY, WC_SECRET)

    )

    return response.json()