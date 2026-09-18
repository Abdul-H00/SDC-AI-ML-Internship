# Test Results — AI Lead Qualification Bot (LangChain)

## Test Case 1
**Input:** `'Hi, I want to buy a new iPhone today, budget is not a problem.'`

**Output:**
```json
{
  "mode": "OFFLINE DEMO (rule-based fallback, no API key found)",
  "input_message": "Hi, I want to buy a new iPhone today, budget is not a problem.",
  "extracted_signals": {
    "budget_mentioned": "high",
    "urgency": "immediate",
    "product_interest": "iphone",
    "intent_to_buy": "strong",
    "reasoning": "Offline rule-based scan found urgency=immediate, budget=high, intent=strong."
  },
  "final_label": "Hot",
  "score_points": 6
}
```

## Test Case 2
**Input:** `'Just browsing, might get a laptop someday, not sure yet.'`

**Output:**
```json
{
  "mode": "OFFLINE DEMO (rule-based fallback, no API key found)",
  "input_message": "Just browsing, might get a laptop someday, not sure yet.",
  "extracted_signals": {
    "budget_mentioned": "unknown",
    "urgency": "exploring",
    "product_interest": "laptop",
    "intent_to_buy": "weak",
    "reasoning": "Offline rule-based scan found urgency=exploring, budget=unknown, intent=weak."
  },
  "final_label": "Cold",
  "score_points": 0
}
```

## Test Case 3
**Input:** `'Need a washing machine urgently, ours broke down today.'`

**Output:**
```json
{
  "mode": "OFFLINE DEMO (rule-based fallback, no API key found)",
  "input_message": "Need a washing machine urgently, ours broke down today.",
  "extracted_signals": {
    "budget_mentioned": "unknown",
    "urgency": "immediate",
    "product_interest": "washing machine",
    "intent_to_buy": "moderate",
    "reasoning": "Offline rule-based scan found urgency=immediate, budget=unknown, intent=moderate."
  },
  "final_label": "Warm",
  "score_points": 3
}
```

## Test Case 4
**Input:** `'Looking for an affordable pair of shoes, tight budget please.'`

**Output:**
```json
{
  "mode": "OFFLINE DEMO (rule-based fallback, no API key found)",
  "input_message": "Looking for an affordable pair of shoes, tight budget please.",
  "extracted_signals": {
    "budget_mentioned": "low",
    "urgency": "unknown",
    "product_interest": "shoes",
    "intent_to_buy": "moderate",
    "reasoning": "Offline rule-based scan found urgency=unknown, budget=low, intent=moderate."
  },
  "final_label": "Cold",
  "score_points": 1
}
```

## Test Case 5
**Input:** `"I'm interested in your premium sofa collection for my new house."`

**Output:**
```json
{
  "mode": "OFFLINE DEMO (rule-based fallback, no API key found)",
  "input_message": "I'm interested in your premium sofa collection for my new house.",
  "extracted_signals": {
    "budget_mentioned": "high",
    "urgency": "unknown",
    "product_interest": "sofa",
    "intent_to_buy": "moderate",
    "reasoning": "Offline rule-based scan found urgency=unknown, budget=high, intent=moderate."
  },
  "final_label": "Warm",
  "score_points": 3
}
```

## Test Case 6
**Input:** `'Can you tell me the store timings?'`

**Output:**
```json
{
  "mode": "OFFLINE DEMO (rule-based fallback, no API key found)",
  "input_message": "Can you tell me the store timings?",
  "extracted_signals": {
    "budget_mentioned": "unknown",
    "urgency": "unknown",
    "product_interest": "not specified",
    "intent_to_buy": "unknown",
    "reasoning": "Offline rule-based scan found urgency=unknown, budget=unknown, intent=unknown."
  },
  "final_label": "Cold",
  "score_points": 0
}
```

## Test Case 7
**Input:** `'I want to order a fridge this week, price should be reasonable.'`

**Output:**
```json
{
  "mode": "OFFLINE DEMO (rule-based fallback, no API key found)",
  "input_message": "I want to order a fridge this week, price should be reasonable.",
  "extracted_signals": {
    "budget_mentioned": "medium",
    "urgency": "soon",
    "product_interest": "fridge",
    "intent_to_buy": "strong",
    "reasoning": "Offline rule-based scan found urgency=soon, budget=medium, intent=strong."
  },
  "final_label": "Hot",
  "score_points": 4
}
```

## Test Case 8
**Input:** `'Just checking prices for now, no rush at all.'`

**Output:**
```json
{
  "mode": "OFFLINE DEMO (rule-based fallback, no API key found)",
  "input_message": "Just checking prices for now, no rush at all.",
  "extracted_signals": {
    "budget_mentioned": "medium",
    "urgency": "immediate",
    "product_interest": "not specified",
    "intent_to_buy": "unknown",
    "reasoning": "Offline rule-based scan found urgency=immediate, budget=medium, intent=unknown."
  },
  "final_label": "Warm",
  "score_points": 3
}
```

## Test Case 9
**Input:** `'Ready to purchase a flagship TV, money is not an issue, want it asap.'`

**Output:**
```json
{
  "mode": "OFFLINE DEMO (rule-based fallback, no API key found)",
  "input_message": "Ready to purchase a flagship TV, money is not an issue, want it asap.",
  "extracted_signals": {
    "budget_mentioned": "high",
    "urgency": "immediate",
    "product_interest": "tv",
    "intent_to_buy": "strong",
    "reasoning": "Offline rule-based scan found urgency=immediate, budget=high, intent=strong."
  },
  "final_label": "Hot",
  "score_points": 6
}
```

## Test Case 10
**Input:** `'Do you have any jackets under 2000 rupees?'`

**Output:**
```json
{
  "mode": "OFFLINE DEMO (rule-based fallback, no API key found)",
  "input_message": "Do you have any jackets under 2000 rupees?",
  "extracted_signals": {
    "budget_mentioned": "low",
    "urgency": "unknown",
    "product_interest": "jacket",
    "intent_to_buy": "unknown",
    "reasoning": "Offline rule-based scan found urgency=unknown, budget=low, intent=unknown."
  },
  "final_label": "Cold",
  "score_points": 0
}
```

## Test Case 11
**Input:** `'Hello'`

**Output:**
```json
{
  "mode": "OFFLINE DEMO (rule-based fallback, no API key found)",
  "input_message": "Hello",
  "extracted_signals": {
    "budget_mentioned": "unknown",
    "urgency": "unknown",
    "product_interest": "not specified",
    "intent_to_buy": "unknown",
    "reasoning": "Offline rule-based scan found urgency=unknown, budget=unknown, intent=unknown."
  },
  "final_label": "Cold",
  "score_points": 0
}
```

## Test Case 12
**Input:** `''`

**Output:**
```json
{
  "error": "Empty message received. Cannot qualify an empty lead."
}
```

## Test Case 13
**Input:** `None`

**Output:**
```json
{
  "error": "No input provided. 'lead_message' cannot be None."
}
```

## Test Case 14
**Input:** `12345`

**Output:**
```json
{
  "error": "Invalid input type: expected str, got int."
}
```

## Test Case 15
**Input:** `'   '`

**Output:**
```json
{
  "error": "Empty message received. Cannot qualify an empty lead."
}
```

