{
  "name": "financial-index",
  "fields": [
    {
      "name": "id",
      "type": "Edm.String",
      "key": true,
      "searchable": false,
      "filterable": false,
      "sortable": false,
      "facetable": false
    },
    {
      "name": "content",
      "type": "Edm.String",
      "searchable": true,
      "filterable": false,
      "sortable": false,
      "facetable": false,
      "analyzer": "es.microsoft"
    },
    {
      "name": "file_name",
      "type": "Edm.String",
      "searchable": true,
      "filterable": true,
      "sortable": true,
      "facetable": true
    },
    {
      "name": "sheet_name",
      "type": "Edm.String",
      "searchable": true,
      "filterable": true,
      "sortable": true,
      "facetable": true
    },
    {
      "name": "period",
      "type": "Edm.String",
      "searchable": true,
      "filterable": true,
      "sortable": true,
      "facetable": true
    },
    {
      "name": "cosmos_id",
      "type": "Edm.String",
      "searchable": false,
      "filterable": true,
      "sortable": false,
      "facetable": false
    },
    {
      "name": "financial_concepts",
      "type": "Collection(Edm.String)",
      "searchable": true,
      "filterable": true,
      "sortable": false,
      "facetable": true
    },
    {
      "name": "has_numeric_data",
      "type": "Edm.Boolean",
      "searchable": false,
      "filterable": true,
      "sortable": false,
      "facetable": true
    },
    {
      "name": "row_number",
      "type": "Edm.Int32",
      "searchable": false,
      "filterable": true,
      "sortable": true,
      "facetable": false
    }
  ],
  "corsOptions": {
    "allowedOrigins": ["*"],
    "maxAgeInSeconds": 60
  },
  "suggesters": [
    {
      "name": "financial-suggester",
      "searchMode": "analyzingInfixMatching",
      "sourceFields": ["content", "financial_concepts"]
    }
  ],
  "semantic": {
    "configurations": [
      {
        "name": "financial-semantic-config",
        "prioritizedFields": {
          "titleField": {
            "fieldName": "file_name"
          },
          "prioritizedContentFields": [
            {
              "fieldName": "content"
            }
          ],
          "prioritizedKeywordsFields": [
            {
              "fieldName": "financial_concepts"
            }
          ]
        }
      }
    ]
  }
}