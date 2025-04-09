# Webhook Endpoint Setup Guide

## Requirements

Your webhook endpoint must meet the following requirements:
- Use POST method
- Accept JSON content type
- Process requests with a `chatInput` field in the body
- Return responses in the specified format

## API Specification

### Request Format
Please ensure your endpoint follows these specifications:
- **Method**: POST
- **Headers**: 
  - Content-Type: application/json
  - Accept: application/json
- **Body**: JSON object with `chatInput` field

### Example Request
```
curl 'https://yourendpoint.com/your-path' 
-H 'Accept: /' 
-H 'Accept-Language: en-GB,en;q=0.9,en-US;q=0.8,ms;q=0.7' 
-H 'Connection: keep-alive' 
-H 'Content-Type: application/json' 
--data-raw '{"chatInput":"test" }'
```

### Response Format
Your endpoint should return a JSON array containing an object with an `output` field.

### Example Response
```
[{"output":"Here is what i found from the knowledge base"}]
```

## Notes
- Refer to the swagger documentation for detailed API specifications
- If you need to modify the request/response format, update the corresponding code in `main.py`
- Ensure your endpoint is accessible and can handle the expected request load 