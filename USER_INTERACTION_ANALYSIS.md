# Database Architecture Analysis: User Interactions & E-Commerce Features

This document provides an architectural analysis for expanding the PJ Store database models to support commercial-grade user interactions. The focus is on features that engage users, such as verified reviews, modern delivery tracking, wishlists, messaging, and returns.

## 1. Verified Product Reviews & Ratings
**Current State:** No review or rating models exist.
**The Issue:** Commercial apps require user feedback, but reviews must be trustworthy. Spam or fake reviews can ruin credibility.
**Recommendation:** Implement a strict, verified review system.
*   **Introduce a `Review` model:**
    *   Fields: `id`, `user_id`, `product_id`, `rating` (1-5), `title`, `comment`, `created_at`, `updated_at`, `is_verified_purchase` (boolean).
    *   **Strict Validation Constraint:** Before creating a review, the system must query the `OrderItem` and `Order` tables to verify:
        1. The `user_id` matches an `Order`.
        2. The `Order` contains the `product_id`.
        3. The `Order.status` is strictly `Delivered`.
    *   *Optional but recommended:* Link the review directly to the `OrderItem` (`order_item_id`). This ensures a user can only leave one review per purchased item and makes the "verified purchase" check explicit via a foreign key constraint.

## 2. Robust Delivery & Fulfillment Tracking
**Current State:** `Order.status` is a simple string (`Pending`, `Paid`, `Shipped`, `Cancelled`).
**The Issue:** Modern e-commerce requires granular tracking. A single string field cannot capture the timeline of fulfillment (e.g., when it was packed, handed to courier, out for delivery) or track the courier's tracking number.
**Recommendation:** Move away from a single state field to an event-driven tracking system.
*   **Introduce an `OrderFulfillment` or `Shipment` model:**
    *   Fields: `id`, `order_id`, `courier_name`, `tracking_number`, `tracking_url`, `estimated_delivery_date`.
*   **Introduce an `OrderEvent` (or `TrackingHistory`) model:**
    *   Fields: `id`, `order_id`, `status_code` (e.g., `ORDER_PLACED`, `PAYMENT_CONFIRMED`, `PACKING`, `SHIPPED`, `OUT_FOR_DELIVERY`, `DELIVERED`, `FAILED_DELIVERY`), `description`, `timestamp`, `location`.
    *   **Why this is modern:** This allows the app to display a timeline of events (like Amazon or Shopify), rather than just a static state. The `Order.status` can become a computed property based on the latest `OrderEvent`, or remain as a high-level summary updated by triggers.

## 3. Wishlists & Favorites
**Current State:** Users can add to a cart, but cannot save items for later.
**The Issue:** Users often browse without immediate intent to buy. Without a wishlist, potential sales are lost.
**Recommendation:** Implement a simple and scalable Wishlist system.
*   **Introduce a `Wishlist` (or `Favorite`) model:**
    *   Fields: `id`, `user_id`, `product_id`, `added_at`.
    *   Constraints: Unique constraint on `(user_id, product_id)` to prevent duplicate entries.
    *   *Alternative:* If users can have multiple named wishlists (e.g., "Birthday", "Gadgets"), use two models: `Wishlist` (`id`, `user_id`, `name`) and `WishlistItem` (`id`, `wishlist_id`, `product_id`). For a standard commercial app, a single default favorites list is usually a good starting point.

## 4. User-to-Seller Messaging / Inquiries
**Current State:** A `Ticket` model exists for global support.
**The Issue:** E-commerce platforms with multiple sellers (like marketplaces) need a way for buyers to ask sellers questions directly about products or specific orders without clogging the global admin support queue.
**Recommendation:** Create a direct messaging system.
*   **Introduce a `MessageThread` (or `Conversation`) model:**
    *   Fields: `id`, `customer_id`, `seller_id`, `product_id` (optional, if related to a specific item), `order_id` (optional), `created_at`, `updated_at`.
*   **Introduce a `Message` model:**
    *   Fields: `id`, `thread_id`, `sender_id`, `content`, `sent_at`, `is_read`.
    *   This separates marketplace communication from platform support (`Ticket`).

## 5. Returns, Refunds, and Disputes
**Current State:** No system to handle post-delivery issues.
**The Issue:** Handling returns is a legal requirement in many jurisdictions and a key part of commercial customer service.
**Recommendation:** Formalize the return process in the database.
*   **Introduce a `ReturnRequest` model:**
    *   Fields: `id`, `order_id` (or `order_item_id` for partial returns), `user_id`, `reason_code` (e.g., `DEFECTIVE`, `WRONG_ITEM`, `CHANGED_MIND`), `description`, `status` (`REQUESTED`, `APPROVED`, `REJECTED`, `RECEIVED`, `REFUNDED`), `created_at`, `resolved_at`.
    *   This works in tandem with the enhanced `Payment` tracking (mentioned in previous financial analyses) to trigger the actual refund via the payment gateway once the `ReturnRequest` is marked `APPROVED` and items are `RECEIVED`.

## 6. User Activity Logging (Audit & Analytics)
**Current State:** Only created_at timestamps exist on standard entities.
**The Issue:** Commercial apps need to understand user behavior (for personalization) and maintain security audit trails (e.g., "When did the user change their shipping address?").
**Recommendation:** Implement an activity feed.
*   **Introduce a `UserActivityLog` model:**
    *   Fields: `id`, `user_id`, `action_type` (e.g., `VIEWED_PRODUCT`, `SEARCHED`, `LOGIN_FAILED`, `UPDATED_PROFILE`), `entity_type` (e.g., `Product`, `Address`), `entity_id`, `metadata` (JSON field containing search queries, old/new values for changes, IP address), `timestamp`.
    *   **Note:** For high-volume systems, this is often stored in a NoSQL database (like MongoDB or Elasticsearch) rather than the primary relational DB to avoid locking and performance degradation, but a basic SQL table is fine for an MVP.