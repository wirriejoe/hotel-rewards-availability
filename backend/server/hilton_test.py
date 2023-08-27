import requests
import json

# url = 'https://www.hilton.com/graphql/customer?appName=dx-res-ui&operationName=hotel_shopAvailOptions_shopPropAvail&originalOpName=getShopAvail&bl=en&ctyhocn=FRAHI'  # Replace this with your GraphQL endpoint URL
url = 'https://www.hilton.com//graphql/customer?appName=dx_shop_search_app&operationName=hotelSummaryOptions_geocodePage&originalOpName=hotelSummaryOptions_geocodePage&bl=en'  # Replace this with your GraphQL endpoint URL
# url = 'https://www.hilton.com/graphql/customer?appName=dx_shop_search_app&operationName=regions&originalOpName=allRegions&bl=en'

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer DX.eyJhbGciOiJSU0EtT0FFUCIsImVuYyI6IkEyNTZHQ00iLCJwaWQiOiJ3ZWIiLCJraWQiOiI4UVl1RTZfdHBValdjUmVnem1RZFlBaF9RYlk1ckVqUlpPTThwWmNKeU5BIn0.ERvjGD5oQf6sQUwzYYmLlMxnYLzVSZO_k8Q9vXM6d-39x6BMJOtfmoGnUfJWKAqkFvF7JhNLET06E46dLhhX8MV-J39lqI17i0fS2xYid98S1aQmiWGx-HxNbVsuAiJwpho4In-jOf8ehXonOIHJuWLr9QmNjYrrY_7BrPBLIAZHWW8_N7VHg_3F6_T0Mvnll4HOgvtgxyZVtUiJix9_QWa1upwjXtPlgoLC7hppXg5koB4iqVBb7l27CuyUUqMWoWTmouylB0uHYRK-kCCFn4OzDqkWR7i6xRWEyhg4Nysk-_EhqYfSOZb8cxHNxzqbyCFILuuKi_4plSj4DvBFkQ.oe2KPkKY2nJR521Q.w0sGWeogUZmwA7IrpCWVsZaV9BMxegT50pcwJWKOPxrf1jvwOItl-Puvr-6djFON62JzCEtZYZg3-03uMkQXmAJIQEjIc_Q0a-bifCacH23Y3_QnAqtuayFHfB5467awag58VZd_0qGKl8tm8WN6JCv1aqfB-oJ1Z5JC5AiPxq3UCUFYaqGbQhitO1HJT7oDl0nr0wQ2nfcGWqe7-Pq6drWmZlQylTURFDcom58ijWfgQ9HhAepHXeOHHi0QotLwy5nIdlffKleL6rL6uv2ypMgYGg6z5vE0AZTVtVkSY6OmVgp89NamAIOmJILGe_OLWdY-ibfwDVUrLvl4dBqmTl7tykVBnyVOFgUW6Lnt8eGkK7y8Dtfhyucu6vKQoij9ycnytq1llQGRKZbVe8JO2_vm-QhKvNi3WOrrPTDJYzFHoCI3MqsKlFrur7xk8Y0cPHPrNKsqdh3EqxvDQ-o2OY16lospnLs4VrAfByATe8_0wLijt4ltshaHOA0Cvq2T6fmiMPR_hwBim9IVVeu-i1d3Mtk4gTp6wnBcOC0JIACoj709zwAKc3slLd0jRTrIMLv0-wa_zXca6qk8PvKSsb6GG9u4DaLagdulYkUcI9bskla8Pt6-ZIGZ6wiz85XPROcUQB7pv_r0PBqN6duQd6q9snU987WrV6ONbcJH4091CLKI2gg.EnJy658IAYddHeOc032mbw'
    # You may also need to include authorization or other headers specific to your API
}

# query = {
#     "query": """
#         query hotel_shopAvailOptions_shopPropAvail($arrivalDate: String!, $ctyhocn: String!, $departureDate: String!, $language: String!, $guestLocationCountry: String, $numAdults: Int!, $numChildren: Int!, $numRooms: Int!, $displayCurrency: String, $guestId: BigInt, $specialRates: ShopSpecialRateInput, $rateCategoryTokens: [String], $selectedRoomRateCodes: [ShopRoomRateCodeInput!], $ratePlanCodes: [String], $pnd: String, $offerId: BigInt, $cacheId: String!, $knownGuest: Boolean, $modifyingReservation: Boolean, $currentlySelectedRoomTypeCode: String, $currentlySelectedRatePlanCode: String, $childAges: [Int], $adjoiningRoomStay: Boolean, $programAccountId: BigInt) {
#         hotel(ctyhocn: $ctyhocn, language: $language) {
#             ctyhocn
#             shopAvailOptions(input: {offerId: $offerId, pnd: $pnd}) {
#             maxNumChildren
#             altCorporateAccount {
#                 corporateId
#                 name
#             }
#             contentOffer {
#                 name
#             }
#             }
#             shopAvail(
#             cacheId: $cacheId
#             input: {guestLocationCountry: $guestLocationCountry, arrivalDate: $arrivalDate, departureDate: $departureDate, displayCurrency: $displayCurrency, numAdults: $numAdults, numChildren: $numChildren, numRooms: $numRooms, guestId: $guestId, specialRates: $specialRates, rateCategoryTokens: $rateCategoryTokens, selectedRoomRateCodes: $selectedRoomRateCodes, ratePlanCodes: $ratePlanCodes, knownGuest: $knownGuest, modifyingReservation: $modifyingReservation, childAges: $childAges, adjoiningRoomStay: $adjoiningRoomStay, programAccountId: $programAccountId}
#             ) {
#             currentlySelectedRoom: roomTypes(
#                 filter: {roomTypeCode: $currentlySelectedRoomTypeCode}
#             ) {
#                 adaAccessibleRoom
#                 roomTypeCode
#                 roomRates(filter: {ratePlanCode: $currentlySelectedRatePlanCode}) {
#                 ratePlanCode
#                 rateAmount
#                 rateAmountFmt(decimal: 0, strategy: trunc)
#                 amountAfterTaxFmt(decimal: 0, strategy: trunc)
#                 fullAmountAfterTax: amountAfterTaxFmt
#                 rateChangeIndicator
#                 ratePlan {
#                     ratePlanName
#                     commissionable
#                     confidentialRates
#                     specialRateType
#                     hhonorsMembershipRequired
#                     salesRate
#                     redemptionType
#                 }
#                 pointDetails {
#                     pointsRateFmt
#                 }
#                 }
#             }
#             statusCode
#             summary {
#                 specialRates {
#                 specialRateType
#                 roomCount
#                 }
#                 requestedRates {
#                 ratePlanCode
#                 ratePlanName
#                 roomCount
#                 }
#             }
#             notifications {
#                 subText
#                 subType
#                 title
#                 text
#             }
#             addOnsAvailable
#             currencyCode
#             roomTypes {
#                 roomTypeCode
#                 adaAccessibleRoom
#                 numBeds
#                 roomTypeName
#                 roomTypeDesc
#                 roomOccupancy
#                 premium
#                 executive
#                 towers
#                 suite
#                 code: roomTypeCode
#                 name: roomTypeName
#                 adjoiningRoom
#                 thumbnail: carousel(first: 1) {
#                 _id
#                 altText
#                 variants {
#                     size
#                     url
#                 }
#                 }
#                 quickBookRate {
#                 cashRatePlan
#                 roomTypeCode
#                 rateAmount
#                 rateChangeIndicator
#                 feeTransparencyIndicator
#                 cmaTotalPriceIndicator
#                 ratePlanCode
#                 rateAmountFmt(decimal: 0, strategy: trunc)
#                 roomTypeCode
#                 amountAfterTaxFmt(decimal: 0, strategy: trunc)
#                 fullAmountAfterTax: amountAfterTaxFmt
#                 ratePlan {
#                     commissionable
#                     confidentialRates
#                     ratePlanName
#                     specialRateType
#                     hhonorsMembershipRequired
#                     salesRate
#                     redemptionType
#                     serviceChargesAndTaxesIncluded
#                 }
#                 serviceChargeDetails
#                 pointDetails(perNight: true) {
#                     pointsRate
#                     pointsRateFmt
#                 }
#                 }
#                 moreRatesFromRate {
#                 rateChangeIndicator
#                 feeTransparencyIndicator
#                 cmaTotalPriceIndicator
#                 roomTypeCode
#                 rateAmount
#                 rateAmountFmt(decimal: 0, strategy: trunc)
#                 amountAfterTaxFmt(decimal: 0, strategy: trunc)
#                 fullAmountAfterTax: amountAfterTaxFmt
#                 serviceChargeDetails
#                 ratePlanCode
#                 ratePlan {
#                     confidentialRates
#                     serviceChargesAndTaxesIncluded
#                 }
#                 }
#                 bookNowRate {
#                 roomTypeCode
#                 rateAmount
#                 rateChangeIndicator
#                 feeTransparencyIndicator
#                 cmaTotalPriceIndicator
#                 ratePlanCode
#                 rateAmountFmt(decimal: 0, strategy: trunc)
#                 amountAfterTaxFmt(decimal: 0, strategy: trunc)
#                 fullAmountAfterTax: amountAfterTaxFmt
#                 roomTypeCode
#                 ratePlan {
#                     commissionable
#                     confidentialRates
#                     ratePlanName
#                     specialRateType
#                     hhonorsMembershipRequired
#                     salesRate
#                     disclaimer {
#                     diamond48
#                     }
#                     serviceChargesAndTaxesIncluded
#                 }
#                 serviceChargeDetails
#                 }
#                 redemptionRoomRates(first: 1) {
#                 rateChangeIndicator
#                 pointDetails(perNight: true) {
#                     pointsRate
#                     pointsRateFmt
#                 }
#                 sufficientPoints
#                 pamEligibleRoomRate {
#                     ratePlan {
#                     ratePlanCode
#                     rateCategoryToken
#                     redemptionType
#                     }
#                     roomTypeCode
#                     sufficientPoints
#                 }
#                 }
#             }
#             lowestPointsInc
#             }
#         }
#         }
#     """,
#     "operationName": "hotel_shopAvailOptions_shopPropAvail",
#     "variables": {
#         "arrivalDate": "2023-08-23",
#         "departureDate": "2023-08-24",
#         "numAdults": 2,
#         "numChildren": 0,
#         "numRooms": 1,
#         "ctyhocn": "FRAHI",
#         "cacheId": "8ece214e-3fe0-47a0-8bb0-012f56fd25d7",
#         "language": "en"
#     }
# }

query = {
    "query": "query hotelSummaryOptions_geocodePage($language: String!, $path: String!, $queryLimit: Int!, $currencyCode: String!, $distanceUnit: HotelDistanceUnit, $titleFormat: MarkdownFormatType!) {\n  geocodePage(language: $language, path: $path) {\n    location {\n      pageInterlinks {\n        title\n        links {\n          name\n          uri\n        }\n      }\n      title(format: $titleFormat)\n      accessibilityTitle\n      meta {\n        pageTitle\n        description\n      }\n      name\n      brandCode\n      category\n      uri\n      globalBounds\n      breadcrumbs {\n        uri\n        name\n      }\n      about {\n        contentBlocks {\n          title(format: text)\n          descriptions\n          orderedList\n          unorderedList\n        }\n      }\n      paths {\n        base\n      }\n    }\n    match {\n      address {\n        city\n        country\n        countryName\n        state\n        stateName\n      }\n      geometry {\n        location {\n          latitude\n          longitude\n        }\n        bounds {\n          northeast {\n            latitude\n            longitude\n          }\n          southwest {\n            latitude\n            longitude\n          }\n        }\n      }\n      name\n      type\n    }\n    hotelSummaryOptions(distanceUnit: $distanceUnit, sortBy: distance) {\n      _hotels {\n        totalSize\n      }\n      bounds {\n        northeast {\n          latitude\n          longitude\n        }\n        southwest {\n          latitude\n          longitude\n        }\n      }\n      amenities {\n        id\n        name\n        hint\n      }\n      amenityCategories {\n        name\n        id\n        amenityIds\n      }\n      brands {\n        code\n        name\n      }\n      hotels(first: $queryLimit) {\n        amenityIds\n        brandCode\n        ctyhocn\n        distance\n        distanceFmt\n        facilityOverview {\n          allowAdultsOnly\n        }\n        name\n        contactInfo {\n          phoneNumber\n        }\n        display {\n          open\n          openDate\n          preOpenMsg\n          resEnabled\n          resEnabledDate\n        }\n        disclaimers {\n          desc\n          type\n        }\n        address {\n          addressFmt\n          addressLine1\n          city\n          country\n          countryName\n          postalCode\n          state\n          stateName\n        }\n        localization {\n          currencyCode\n          coordinate {\n            latitude\n            longitude\n          }\n        }\n        masterImage(variant: searchPropertyImageThumbnail) {\n          altText\n          variants {\n            size\n            url\n          }\n        }\n        leadRate {\n          lowest {\n            rateAmount(currencyCode: $currencyCode)\n            rateAmountFmt(decimal: 0, strategy: trunc)\n            ratePlanCode\n            ratePlan {\n              ratePlanName\n              ratePlanDesc\n            }\n          }\n        }\n      }\n    }\n  }\n}",
    "operationName": "hotelSummaryOptions_geocodePage",
    "variables": {
        "path": "locations/united-kingdom",
        "language": "en",
        "queryLimit": 150,
        "currencyCode": "USD",
        "titleFormat": "md"
    }
}

# query = {
#     "query": "query regions($language: String!) {\n  na: regions(\n    language: $language\n    containsHotels: true\n    filter: {htmlSiteMap: true, name: \"North America\"}\n  ) {\n    name\n    locationPageUri\n    countries {\n      code\n      name\n      locationPageUri\n      displayName\n      states(sort: {by: name, order: asc}) {\n        name\n        locationPageUri\n      }\n      cities(sort: {by: name, order: asc}, onlyIfNoStates: true) {\n        name\n        locationPageUri\n      }\n    }\n  }\n  others: regions(\n    language: $language\n    containsHotels: true\n    filter: {htmlSiteMap: true, name_not: \"North America\"}\n  ) {\n    name\n    locationPageUri\n    countries(sort: {by: name, order: asc}) {\n      code\n      name\n      locationPageUri\n      displayName\n      states {\n        name\n        locationPageUri\n      }\n    }\n  }\n}",
#     "operationName": "regions",
#     "variables": {
#         "language": "en"
#     }
# }

response = requests.post(url, json=query, headers=headers)

if response.status_code == 200:
    print("Success!")
    response_json = response.json()

    with open("response.json", "w") as f:
        json.dump(response_json, f)

    # print(json.dumps(response.json(), indent=4))
else:
    print("Failed!")
    print(response.text)