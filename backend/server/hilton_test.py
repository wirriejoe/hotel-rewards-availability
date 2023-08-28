import requests
import json

url = 'https://www.hilton.com/graphql/customer?appName=dx-res-ui&operationName=hotel_shopAvailOptions_shopPropAvail&originalOpName=getShopAvail&bl=en&ctyhocn=FRAHI'  # Replace this with your GraphQL endpoint URL

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer DX.eyJhbGciOiJSU0EtT0FFUCIsImVuYyI6IkEyNTZHQ00iLCJwaWQiOiJ3ZWIiLCJraWQiOiI4UVl1RTZfdHBValdjUmVnem1RZFlBaF9RYlk1ckVqUlpPTThwWmNKeU5BIn0.fTfFgf5o1onJG3fLdILtJ67aD9q1HlAg-9c9_AneFLybRW50wmsNJsQnCDB0Qi-L7W1BsYtXm01kgi89V6wVO2LqhNMY_L2HPMyznWkD8eYvl9gvMflOt35EGhHelRsiu0fD9spVy_ABDqJS41ZfWGQPXq68Yu-tVQk6Po3swfAkfzTakR1cUWjTQszKwAfWbFD-0IKnz7k_O0rHNBBHil4e6oKHsx9e__V1o9qNCxL5JR9NkXE764IBD_A62V5P6I6DyO29XNQB7oOQuLZGtoiiJ772W2FQZw_8-El_4EONT09NaQx6faQsgs4qVDnIXevjCL-i4FpSi0D7cB4-wQ.CflbNsj2TCl0uXB4.j04B7oosy-Va_0JzV43T1vAkpNVfzk_QDJtyc2vb6cdTHNANlXKJ2U32fJb-fMxO6y2cqnqygHIAZXpgAna8gN-JdaA5ekreMRtQSVQgcznDtgVkM57R9DQCkPUF1PIsRTu-xT86zU0AHoHi4xgNnGXwEipKqB4ZIlveUzSQiNv5h-BUyByxjI4HUwcXAdYwNdWG5_MqYjx25eHrh7gJ__QeotVoFWWPov1JiIFUcxao5qLNGRVV6q3aT7IshmHJxOMxtwXIbL5P4mhffaAYLuXLNpyodAL-UnTaPhflLGQ29iEEJXqwgnZORFzvWeW8e6c1l8j-4w712jjFWQ0xvFzB87jtNCqltypKOUwsUbovdAx-tz7xs9KXuFxg9IJf-EMvJLzPNOPHPSKu5ROQrCiFOouixwIhBhUjgTtmIrxg3AIkhqtbjEu8L3on072e_qeGICyJJYtiDFjPlhEDbZYpivHu01d8PvDW67AsRKkhckSl_wMxg8CPQLWj2FBszTEDkwSpwtsB41oXTuAJoCmMZ_viHFRqhPYORMwXebOtPuMRo3IZjlL1eEfkXygTpj67-I499nLIrATJw8450pP-y4Xrr3djUEwrcVEV2XTqXhUea5M5Aic5Hz1U5R95-FcTKutTQeBMOJeE4_UxtLWVHghqN81jL5bH6FyQQiJBhAnx5tE.9aTOvTURpuNrb00aVHj__w'
    # You may also need to include authorization or other headers specific to your API
}

query = {
    "query": """
        query hotel_shopAvailOptions_shopPropAvail($arrivalDate: String!, $ctyhocn: String!, $departureDate: String!, $language: String!, $guestLocationCountry: String, $numAdults: Int!, $numChildren: Int!, $numRooms: Int!, $displayCurrency: String, $guestId: BigInt, $specialRates: ShopSpecialRateInput, $rateCategoryTokens: [String], $selectedRoomRateCodes: [ShopRoomRateCodeInput!], $ratePlanCodes: [String], $pnd: String, $offerId: BigInt, $cacheId: String!, $knownGuest: Boolean, $modifyingReservation: Boolean, $currentlySelectedRoomTypeCode: String, $currentlySelectedRatePlanCode: String, $childAges: [Int], $adjoiningRoomStay: Boolean, $programAccountId: BigInt) {
        hotel(ctyhocn: $ctyhocn, language: $language) {
            ctyhocn
            shopAvailOptions(input: {offerId: $offerId, pnd: $pnd}) {
            maxNumChildren
            altCorporateAccount {
                corporateId
                name
            }
            contentOffer {
                name
            }
            }
            shopAvail(
            cacheId: $cacheId
            input: {guestLocationCountry: $guestLocationCountry, arrivalDate: $arrivalDate, departureDate: $departureDate, displayCurrency: $displayCurrency, numAdults: $numAdults, numChildren: $numChildren, numRooms: $numRooms, guestId: $guestId, specialRates: $specialRates, rateCategoryTokens: $rateCategoryTokens, selectedRoomRateCodes: $selectedRoomRateCodes, ratePlanCodes: $ratePlanCodes, knownGuest: $knownGuest, modifyingReservation: $modifyingReservation, childAges: $childAges, adjoiningRoomStay: $adjoiningRoomStay, programAccountId: $programAccountId}
            ) {
            currentlySelectedRoom: roomTypes(
                filter: {roomTypeCode: $currentlySelectedRoomTypeCode}
            ) {
                adaAccessibleRoom
                roomTypeCode
                roomRates(filter: {ratePlanCode: $currentlySelectedRatePlanCode}) {
                ratePlanCode
                rateAmount
                rateAmountFmt(decimal: 0, strategy: trunc)
                amountAfterTaxFmt(decimal: 0, strategy: trunc)
                fullAmountAfterTax: amountAfterTaxFmt
                rateChangeIndicator
                ratePlan {
                    ratePlanName
                    commissionable
                    confidentialRates
                    specialRateType
                    hhonorsMembershipRequired
                    salesRate
                    redemptionType
                }
                pointDetails {
                    pointsRateFmt
                }
                }
            }
            statusCode
            summary {
                specialRates {
                specialRateType
                roomCount
                }
                requestedRates {
                ratePlanCode
                ratePlanName
                roomCount
                }
            }
            notifications {
                subText
                subType
                title
                text
            }
            addOnsAvailable
            currencyCode
            roomTypes {
                roomTypeCode
                adaAccessibleRoom
                numBeds
                roomTypeName
                roomTypeDesc
                roomOccupancy
                premium
                executive
                towers
                suite
                code: roomTypeCode
                name: roomTypeName
                adjoiningRoom
                thumbnail: carousel(first: 1) {
                _id
                altText
                variants {
                    size
                    url
                }
                }
                quickBookRate {
                cashRatePlan
                roomTypeCode
                rateAmount
                rateChangeIndicator
                feeTransparencyIndicator
                cmaTotalPriceIndicator
                ratePlanCode
                rateAmountFmt(decimal: 0, strategy: trunc)
                roomTypeCode
                amountAfterTaxFmt(decimal: 0, strategy: trunc)
                fullAmountAfterTax: amountAfterTaxFmt
                ratePlan {
                    commissionable
                    confidentialRates
                    ratePlanName
                    specialRateType
                    hhonorsMembershipRequired
                    salesRate
                    redemptionType
                    serviceChargesAndTaxesIncluded
                }
                serviceChargeDetails
                pointDetails(perNight: true) {
                    pointsRate
                    pointsRateFmt
                }
                }
                moreRatesFromRate {
                rateChangeIndicator
                feeTransparencyIndicator
                cmaTotalPriceIndicator
                roomTypeCode
                rateAmount
                rateAmountFmt(decimal: 0, strategy: trunc)
                amountAfterTaxFmt(decimal: 0, strategy: trunc)
                fullAmountAfterTax: amountAfterTaxFmt
                serviceChargeDetails
                ratePlanCode
                ratePlan {
                    confidentialRates
                    serviceChargesAndTaxesIncluded
                }
                }
                bookNowRate {
                roomTypeCode
                rateAmount
                rateChangeIndicator
                feeTransparencyIndicator
                cmaTotalPriceIndicator
                ratePlanCode
                rateAmountFmt(decimal: 0, strategy: trunc)
                amountAfterTaxFmt(decimal: 0, strategy: trunc)
                fullAmountAfterTax: amountAfterTaxFmt
                roomTypeCode
                ratePlan {
                    commissionable
                    confidentialRates
                    ratePlanName
                    specialRateType
                    hhonorsMembershipRequired
                    salesRate
                    disclaimer {
                    diamond48
                    }
                    serviceChargesAndTaxesIncluded
                }
                serviceChargeDetails
                }
                redemptionRoomRates(first: 1) {
                rateChangeIndicator
                pointDetails(perNight: true) {
                    pointsRate
                    pointsRateFmt
                }
                sufficientPoints
                pamEligibleRoomRate {
                    ratePlan {
                    ratePlanCode
                    rateCategoryToken
                    redemptionType
                    }
                    roomTypeCode
                    sufficientPoints
                }
                }
            }
            lowestPointsInc
            }
        }
        }
    """,
    "operationName": "hotel_shopAvailOptions_shopPropAvail",
    "variables": {
        "arrivalDate": "2023-08-28",
        "departureDate": "2023-08-29",
        "numAdults": 2,
        "numChildren": 0,
        "numRooms": 1,
        "ctyhocn": "LAXWAWA",
        "cacheId": "8ece214e-3fe0-47a0-8bb0-012f56fd25d7",
        "language": "en"
    }
}

response = requests.post(url, json=query, headers=headers)



if response.status_code == 200:
    print("Success!")
    response_json = response.json()
    with open("response.json", "w") as f:
        json.dump(response_json, f)
else:
    print("Failed!")
    print(response.text)