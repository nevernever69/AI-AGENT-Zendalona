# Admin Panel Documentation

This document provides an overview of the admin panel features, including the relevant files, API endpoints, and their descriptions.

## Authentication

- **File:** `routers/auth.py`
- **Description:** Handles user authentication for the admin panel.

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | /auth/login | Authenticates a user and returns an access token. |
| GET | /auth/me | Returns the current authenticated user. |

## Cache Management

- **File:** `routers/cache.py`
- **Description:** Manages the permanent cache for chatbot responses.

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | /cache/add | Adds a new question-answer pair to the cache. |
| PUT | /cache/update/{entry_id} | Updates an existing cache entry. |
| POST | /cache/import | Imports cache entries from a CSV file. |
| GET | /cache/export | Exports all cache entries to a CSV file. |
| DELETE | /cache/delete/{entry_id} | Deletes a cache entry. |
| GET | /cache/count | Returns the total number of cache entries. |
| GET | /cache/summary | Returns a summary of the cache entries. |
| GET | /cache/check/{question} | Checks if a question exists in the cache. |

## Chat

- **File:** `routers/chat.py`
- **Description:** Handles the main chatbot functionality.

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | /chat | Processes a chat query and returns a complete response. |
| POST | /chat/stream | Streams a chat response in real-time. |
| POST | /chat/feedback | Submits feedback for a chat response. |
| DELETE | /chat/sessions/{session_id} | Deletes a chat session. |
| GET | /chat/sessions | Lists all active chat sessions. |

## Feedback Management

- **File:** `routers/feedback.py`
- **Description:** Manages user feedback for chatbot responses.

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | /feedback | Returns all feedback items. |
| DELETE | /feedback/{item_id} | Deletes a feedback item. |
| POST | /feedback/move-to-cache/{item_id} | Updates a feedback item and moves it to the permanent cache. |

## Indexing

- **File:** `routers/indexing.py`
- **Description:** Manages the indexing of documents for the chatbot.

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | /indexing/crawl | Crawls and indexes a website. |
| POST | /indexing/import | Imports and processes a file. |
| POST | /indexing/upload-pdf | Uploads and processes a PDF file. |
| GET | /indexing/collections | Lists all collections. |
| DELETE | /indexing/collections/{collection_name} | Deletes a collection. |
| GET | /indexing/cache | Returns all cache entries. |
| DELETE | /indexing/cache/{entry_id} | Deletes a cache entry. |
| GET | /indexing/collections/{collection_name} | Returns all documents from a collection. |
| DELETE | /indexing/collections/{collection_name}/{document_id} | Deletes a document from a collection. |

## System

- **File:** `routers/system.py`
- **Description:** Provides system information and health checks.

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | /system/health | Returns the health status of the API. |
| GET | /system/info | Returns detailed system information. |

## Temporary Cache Management

- **File:** `routers/temp_cache.py`
- **Description:** Manages the temporary cache for chatbot responses.

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | /temp-cache | Returns all temporary cache items. |
| PUT | /temp-cache/{item_id} | Updates a temporary cache item. |
| POST | /temp-cache/move/{item_id} | Moves a temporary cache item to the permanent cache. |
| PUT | /temp-cache/update-and-move/{item_id} | Updates a temporary cache item and moves it to the permanent cache. |
| DELETE | /temp-cache/{item_id} | Deletes a temporary cache item. |
