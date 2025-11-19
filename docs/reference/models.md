# Data Models

This page contains all the data models used in the API.

## HTTPValidationError

**Schema:**
```json
{
  "detail": [ValidationError]  // 
}
```

**Properties:**

- **detail**: `[ValidationError]`

---

## NewEndpointRequest

**Schema:**
```json
{
  "name": string (required)  // The name to include in the message.
}
```

**Properties:**

- **name** *(required)*: `string`
  - Description: The name to include in the message.
  - Example: `developer`

---

## NewEndpointResponse

**Schema:**
```json
{
  "message": string (required)  // A welcome message.
}
```

**Properties:**

- **message** *(required)*: `string`
  - Description: A welcome message.
  - Example: `Hello, world!`

---

## ValidationError

**Schema:**
```json
{
  "loc": [unknown] (required)  // 
  "msg": string (required)  // 
  "type": string (required)  // 
}
```

**Properties:**

- **loc** *(required)*: `[unknown]`

- **msg** *(required)*: `string`

- **type** *(required)*: `string`

---
