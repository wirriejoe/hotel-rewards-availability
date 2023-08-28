import requests
import json

# Will be useful for refreshing auth tokens using selenium https://gist.github.com/rengler33/f8b9d3f26a518c08a414f6f86109863c

url = 'https://www.hilton.com/graphql/customer?appName=dx-res-ui&operationName=hotel_shopAvailOptions_shopPropAvail&originalOpName=getShopAvail&bl=en&ctyhocn=BJSCAHI'  # Replace this with your GraphQL endpoint URL

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer DX.eyJhbGciOiJSU0EtT0FFUCIsImVuYyI6IkEyNTZHQ00iLCJwaWQiOiJ3ZWIiLCJraWQiOiI4UVl1RTZfdHBValdjUmVnem1RZFlBaF9RYlk1ckVqUlpPTThwWmNKeU5BIn0.Mj0NZUxtoEyAhjR_wH6ZDC7Mn4ZlcnkEF0JIg850GOfG8n-xBrTS0s2mHWjOxD-irJuQEMYlY2l52Q1cC2ikqTqM-WS9kPz5ZC68GVqQ4Ub-TkGi8D_XxGMCDWkveCupHV3a2c-WonEA3AyVwfYKhG2EZNIQIdrnAi8Xr7Mg9mPxyogTF3m8M5Wwnagu69Z3YcNf28gXkjrUkgRf7pdFDnqCzgsKylZsIV4KMwOQ6KA7HL7b1ehJi36Ncx89zIOU0L3_lVgmCbs0mmySmjhQt23acFlCOUSaKZ2eO5N3OYCE1-kyrIhrMh-m-mKZuF3NQC1gufuYDbAQ7-fF46ynyQ.eY___-PJ5EQK-vlN.7-E-qbM-Vo3FFVdmxKy48FTv_Q-bhZ9tWYuhTwuxEC6pXSGVYlrs3Ges8my0OpuIEO7jgnFG3xlNoJ_sTtxbXV69NeEBzthrOkVb8PVjp6SfO-BMuM6WFUAoiXZYK3cwfRNSM74exCon8h1iCHIch20RAdiVaGVUz_HSKypuxRNR4XEBZV_0DQR5iY90Un-xJCs6yt1Z4XoOGdVpXLhT06YWLo63Pny-NstsBmCTOJos87cVOcXU_uqWcM8vj2btNDSUxGt6-Q1WUIOAwIb4Bvsyk4Irc__xdkdQAXGXYvEWcpmtwm2xY_b-Va90MdQ3qcMiZ6ACBImzGEGWlPnjbcz5nk1cBOYk6lP_7PrrvDDDMo2iYqaHPHHy5A-8zJZobuZzUE19b7hhhuLlIMglkwDiNfDv7IvXAoM481E5sMxY8n0DqjVwxafgMCcIOcxJdfAkXHnIKkayOj_Ggwq12tCIGIlseha9kDIWO3xx-x4raHbglxdHdiSMxixTKFEuXVrivht3UFvnLNTGaWU2ojZ7e1qZ44Uc1gW4fuD61auU9h3Nj-jgP59EnuIl2qc2mWh_kuC-ar-8NO71lcqxSFj-KYnIFkuchCYaZHroPT1qcBsudbA8Q-j7c1K-TRyNPn85-FpgCcDEhHHY8ZTmE27eBOVI0Oa8OWZPeUiIv4DLwXOPUHAhZHTMweMLwoJpx88cnJRZ3blSpAkoUJnKJh6JLsYLpkokqtkCDY7RkhHsQ5NbPf5Xv9Hp6qzroULlTUOpJ5fDjXGXfB5WRsqgriCHOB75voz2-N4f73nEPhfwI-Tu6iYUdeUQxdaBSpjcSmXIj6nYPEpPCqTqjwGWBFUehN7um3oVjUm-T6vhzQfCZRVgfiwP90kyLpHiHmJmIyhFAY7b_BKN3b7FtubjfFCndBd9dOJnJpcL7OrlFWoU3Lt6sV_sQRuWs8vOsdFfbgisQWg2kyK-vJuK0kCsCnYkGhq7dEOUbGZ1EmD18g5dkbulYXIcrjYqqgLF4YatJ5zWIjUlXsM66imkz3v-tyEGby8PKnxXsBzDWmNS7h2s9PrjUnw7npaebi0mOgeJs8wk5pTy8vj6giCfB7duwuQuxsC9eMSjlzgNUcmhOALhHnsV3McdXIaZF3pVZ0PyWNo.Q4jFFEZZ0TizkyV0ePLKng'
    # You may also need to include authorization or other headers specific to your API
}

check_in_date = "2023-08-28"
check_out_date = "2023-08-29"

query = {
    "query": "query hotel_shopAvailOptions_shopPropAvail($arrivalDate: String!, $ctyhocn: String!, $departureDate: String!, $language: String!, $guestLocationCountry: String, $numAdults: Int!, $numChildren: Int!, $numRooms: Int!, $displayCurrency: String, $guestId: BigInt, $specialRates: ShopSpecialRateInput, $rateCategoryTokens: [String], $selectedRoomRateCodes: [ShopRoomRateCodeInput!], $ratePlanCodes: [String], $pnd: String, $offerId: BigInt, $cacheId: String!, $knownGuest: Boolean, $modifyingReservation: Boolean, $currentlySelectedRoomTypeCode: String, $currentlySelectedRatePlanCode: String, $childAges: [Int], $adjoiningRoomStay: Boolean, $programAccountId: BigInt) {\n  hotel(ctyhocn: $ctyhocn, language: $language) {\n    ctyhocn\n    shopAvailOptions(input: {offerId: $offerId, pnd: $pnd}) {\n      maxNumChildren\n      altCorporateAccount {\n        corporateId\n        name\n      }\n      contentOffer {\n        name\n      }\n    }\n    shopAvail(\n      cacheId: $cacheId\n      input: {guestLocationCountry: $guestLocationCountry, arrivalDate: $arrivalDate, departureDate: $departureDate, displayCurrency: $displayCurrency, numAdults: $numAdults, numChildren: $numChildren, numRooms: $numRooms, guestId: $guestId, specialRates: $specialRates, rateCategoryTokens: $rateCategoryTokens, selectedRoomRateCodes: $selectedRoomRateCodes, ratePlanCodes: $ratePlanCodes, knownGuest: $knownGuest, modifyingReservation: $modifyingReservation, childAges: $childAges, adjoiningRoomStay: $adjoiningRoomStay, programAccountId: $programAccountId}\n    ) {\n      currentlySelectedRoom: roomTypes(\n        filter: {roomTypeCode: $currentlySelectedRoomTypeCode}\n      ) {\n        adaAccessibleRoom\n        roomTypeCode\n        roomRates(filter: {ratePlanCode: $currentlySelectedRatePlanCode}) {\n          ratePlanCode\n          rateAmount\n          rateAmountFmt(decimal: 0, strategy: trunc)\n          amountAfterTaxFmt(decimal: 0, strategy: trunc)\n          fullAmountAfterTax: amountAfterTaxFmt\n          rateChangeIndicator\n          ratePlan {\n            ratePlanName\n            commissionable\n            confidentialRates\n            specialRateType\n            hhonorsMembershipRequired\n            salesRate\n            redemptionType\n          }\n          pointDetails {\n            pointsRateFmt\n          }\n        }\n      }\n      statusCode\n      summary {\n        specialRates {\n          specialRateType\n          roomCount\n        }\n        requestedRates {\n          ratePlanCode\n          ratePlanName\n          roomCount\n        }\n      }\n      notifications {\n        subText\n        subType\n        title\n        text\n      }\n      addOnsAvailable\n      currencyCode\n      roomTypes {\n        roomTypeCode\n        adaAccessibleRoom\n        numBeds\n        roomTypeName\n        roomTypeDesc\n        roomOccupancy\n        premium\n        executive\n        towers\n        suite\n        code: roomTypeCode\n        name: roomTypeName\n        adjoiningRoom\n        thumbnail: carousel(first: 1) {\n          _id\n          altText\n          variants {\n            size\n            url\n          }\n        }\n        quickBookRate {\n          cashRatePlan\n          roomTypeCode\n          rateAmount\n          rateChangeIndicator\n          feeTransparencyIndicator\n          cmaTotalPriceIndicator\n          ratePlanCode\n          rateAmountFmt(decimal: 0, strategy: trunc)\n          roomTypeCode\n          amountAfterTaxFmt(decimal: 0, strategy: trunc)\n          fullAmountAfterTax: amountAfterTaxFmt\n          ratePlan {\n            commissionable\n            confidentialRates\n            ratePlanName\n            specialRateType\n            hhonorsMembershipRequired\n            salesRate\n            redemptionType\n            serviceChargesAndTaxesIncluded\n          }\n          serviceChargeDetails\n          pointDetails(perNight: true) {\n            pointsRate\n            pointsRateFmt\n          }\n        }\n        moreRatesFromRate {\n          rateChangeIndicator\n          feeTransparencyIndicator\n          cmaTotalPriceIndicator\n          roomTypeCode\n          rateAmount\n          rateAmountFmt(decimal: 0, strategy: trunc)\n          amountAfterTaxFmt(decimal: 0, strategy: trunc)\n          fullAmountAfterTax: amountAfterTaxFmt\n          serviceChargeDetails\n          ratePlanCode\n          ratePlan {\n            confidentialRates\n            serviceChargesAndTaxesIncluded\n          }\n        }\n        bookNowRate {\n          roomTypeCode\n          rateAmount\n          rateChangeIndicator\n          feeTransparencyIndicator\n          cmaTotalPriceIndicator\n          ratePlanCode\n          rateAmountFmt(decimal: 0, strategy: trunc)\n          amountAfterTaxFmt(decimal: 0, strategy: trunc)\n          fullAmountAfterTax: amountAfterTaxFmt\n          roomTypeCode\n          ratePlan {\n            commissionable\n            confidentialRates\n            ratePlanName\n            specialRateType\n            hhonorsMembershipRequired\n            salesRate\n            disclaimer {\n              diamond48\n            }\n            serviceChargesAndTaxesIncluded\n          }\n          serviceChargeDetails\n        }\n        redemptionRoomRates(first: 1) {\n          rateChangeIndicator\n          pointDetails(perNight: true) {\n            pointsRate\n            pointsRateFmt\n          }\n          sufficientPoints\n          pamEligibleRoomRate {\n            ratePlan {\n              ratePlanCode\n              rateCategoryToken\n              redemptionType\n            }\n            roomTypeCode\n            sufficientPoints\n          }\n        }\n      }\n      lowestPointsInc\n    }\n  }\n}",
    "operationName": "hotel_shopAvailOptions_shopPropAvail",
    "variables": {
        "arrivalDate": "2023-08-28",
        "departureDate": "2023-08-29",
        "numAdults": 2,
        "numChildren": 0,
        "numRooms": 1,
        "ctyhocn": "BJSCAHI",
        "language": "en",
        "specialRates": {
            # "aaa": False,
            # "aarp": False,
            # "governmentMilitary": False,
            "hhonors": True,
            # "pnd": "",
            # "senior": False,
            # "teamMember": False,
            # "owner": False,
            # "ownerHGV": False,
            # "familyAndFriends": False,
            # "travelAgent": False,
            # "smb": False,
            # "specialOffer": False,
        },
        "cacheId": "d4617320-b176-4c26-934f-7216ac72b7aa"
    }
}

response = requests.post(url, json=query, headers=headers)

awards = response.json()['data']['hotel']['shopAvail']['roomTypes']

for award in awards:
    room_type_code = award['roomTypeCode']
    room_name = award['name']
    room_category = 'Suite' if award['suite'] else 'Standard'
    # lowest_points_rate = 


if response.status_code == 200:
    print("Success!")
    response_json = response.json()
    with open("response.json", "w") as f:
        json.dump(response_json, f)
else:
    print("Failed!")
    print(response.text)