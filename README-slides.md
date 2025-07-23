# Google Drive API - Slides Service

This document provides a comprehensive guide to using the Slides API, a service designed to create and manage Google Slides presentations with rich content, including styled text and tables.

## API Overview

The Slides API provides a set of RESTful endpoints for interacting with Google Slides. It allows you to:

- Create new, empty presentations.
- Retrieve the content of existing presentations in a simplified format.
- Add new slides with predefined layouts.
- Insert text boxes with custom styling.
- Add tables with specified dimensions and data.

All endpoints are organized under the `/drive/presentations` resource path and require session-based authentication.

---

## Endpoints

### 1. Create a Presentation

- **`POST /drive/presentations`**

  Creates a new, empty Google Slides presentation with a specified title.

  **Request Body:**

  ```json
  {
    "title": "Your Presentation Title"
  }
  ```

  **Example `curl` Request:**

  ```bash
  curl -X POST "http://localhost:8000/drive/presentations" \
  -H "Content-Type: application/json" \
  -H "Cookie: session=<SESSION_COOKIE_VALUE>" \
  -d '{"title": "My New Presentation"}'
  ```

### 2. Get a Presentation

- **`GET /drive/presentations/{presentation_id}`**

  Retrieves a presentation in a simplified format, including its ID, title, and a list of slides with their content.

  **Example `curl` Request:**

  ```bash
  curl -X GET "http://localhost:8000/drive/presentations/<PRESENTATION_ID>" \
  -H "Cookie: session=<SESSION_COOKIE_VALUE>"
  ```

### 3. Add a Slide

- **`POST /drive/presentations/{presentation_id}/slides`**

  Adds a new slide to an existing presentation. You can specify a layout and add content, including styled text and tables.

  **Request Body:**

  The request body is a `SlidePayload` object. You must specify a `layout`. You can also provide simple text for `title`, `subtitle`, and `body` placeholders, or use the `texts` and `tables` arrays for more complex content.

  **Example `curl` Request (with styled text and a table):**

  ```bash
  curl -X POST "http://localhost:8000/drive/presentations/<PRESENTATION_ID>/slides" \
  -H "Content-Type: application/json" \
  -H "Cookie: session=<SESSION_COOKIE_VALUE>" \
  -d '{
    "layout": "TITLE_AND_BODY",
    "title": "Slide with Rich Content",
    "texts": [
      {
        "text": "This is a styled text box.",
        "style": {
          "font_family": "Arial",
          "font_size": 24,
          "bold": true,
          "foreground_color": { "red": 0.0, "green": 0.0, "blue": 1.0 }
        }
      }
    ],
    "tables": [
      {
        "rows": 2,
        "columns": 2,
        "data": [
          ["Header 1", "Header 2"],
          ["Data 1", "Data 2"]
        ]
      }
    ]
  }'
  ```

### 4. Delete a Slide

- **`DELETE /drive/presentations/{presentation_id}/slides/{slide_id}`**

  Deletes a specific slide from a presentation.

  **Example `curl` Request:**

  ```bash
  curl -X DELETE "http://localhost:8000/drive/presentations/<PRESENTATION_ID>/slides/<SLIDE_ID>" \
  -H "Cookie: session=<SESSION_COOKIE_VALUE>"
  ```

---

## Data Models

### `SlidePayload`

| Key        | Type                  | Description                                                                                                                              |
|------------|-----------------------|------------------------------------------------------------------------------------------------------------------------------------------|
| `layout`   | string                | **Required.** The predefined layout for the slide (e.g., `TITLE_SLIDE`, `TITLE_AND_BODY`).                                              |
| `title`    | string                | Text for the main title placeholder.                                                                                                     |
| `subtitle` | string                | Text for the subtitle placeholder.                                                                                                       |
| `body`     | string                | Text for the body placeholder.                                                                                                           |
| `texts`    | array of `TextPayload`| A list of styled text boxes to add to the slide.                                                                                         |
| `tables`   | array of `TablePayload`| A list of tables to add to the slide.                                                                                                    |

### `TextPayload`

| Key         | Type        | Description                                      |
|-------------|-------------|--------------------------------------------------|
| `text`      | string      | The content of the text box.                     |
| `style`     | `TextStyle` | The styling to apply to the text.                |
| `element_id`| string      | An optional unique identifier for the text box.  |

### `TablePayload`

| Key         | Type     | Description                                   |
|-------------|----------|-----------------------------------------------|
| `rows`      | integer  | The number of rows in the table.              |
| `columns`   | integer  | The number of columns in the table.           |
| `data`      | array    | A 2D array of strings representing cell data. |
| `element_id`| string   | An optional unique identifier for the table.  |

### `TextStyle`

| Key                | Type      | Description                               |
|--------------------|-----------|-------------------------------------------|
| `font_family`      | string    | The font family (e.g., "Arial", "Times New Roman"). |
| `font_size`        | integer   | The font size in points.                  |
| `bold`             | boolean   | Whether the text is bold.                 |
| `italic`           | boolean   | Whether the text is italic.               |
| `underline`        | boolean   | Whether the text is underlined.           |
| `strikethrough`    | boolean   | Whether the text has a strikethrough.     |
| `foreground_color` | `Color`   | The color of the text.                    |

### `Color`

| Key     | Type  | Description                        |
|---------|-------|------------------------------------|
| `red`   | float | The red component (0.0 to 1.0).    |
| `green` | float | The green component (0.0 to 1.0).  |
| `blue`  | float | The blue component (0.0 to 1.0).   | 