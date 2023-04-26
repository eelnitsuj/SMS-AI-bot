curl -X POST https://api.postscript.io/webhooks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk_d295fe89a5ec7cd1a81a4a7daf01ca0d" \
  -d '{
    "webhook": {
      "url": "https://infinite-castle-46811.herokuapp.com/",
      "event": "inbound_sms"
    }
  }'

Invoke-WebRequest -Uri "https://api.postscript.io/api/v2/webhooks" `
  -Method POST `
  -Headers @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer sk_d295fe89a5ec7cd1a81a4a7daf01ca0d"
  } `
  -Body '{
    "webhook": {
      "url": "https://infinite-castle-46811.herokuapp.com/",
      "event": "inbound_sms"
    }
  }'

Invoke-WebRequest -Uri "https://api.postscript.io/v2/webhooks" `
  -Method POST `
  -Headers @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer sk_d295fe89a5ec7cd1a81a4a7daf01ca0d"
  } `
  -Body (@{
    "webhook" = @{
      "url" = "https://infinite-castle-46811.herokuapp.com/"
      "event" = "inbound_sms"
    }
  } | ConvertTo-Json)