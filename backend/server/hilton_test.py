import requests
import json

url = 'https://www.hilton.com/graphql/customer?appName=dx-res-ui&operationName=hotel_shopAvailOptions_shopPropAvail&originalOpName=getShopAvail&bl=en&ctyhocn=FRAHI'  # Replace this with your GraphQL endpoint URL

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer DX.eyJhbGciOiJSU0EtT0FFUCIsImVuYyI6IkEyNTZHQ00iLCJwaWQiOiJ3ZWIiLCJraWQiOiI4UVl1RTZfdHBValdjUmVnem1RZFlBaF9RYlk1ckVqUlpPTThwWmNKeU5BIn0.X2wpw9Z3_vWiTU6eRw2K8vzdguAS0SlYRB0-aIaLURWAp7Y4ae7SByqjUFaJ2GFMfA3g4C9vxWuiJG2Mh_6zFAOgfWmpJjlUANYPVyGDY0AjSvStbqWqseJ8PGRjtpAdGxpb3WwFj-efaisMal4HWjuOcML-MiVNueRm5f2E4wALPp80LPRuhPcGez7_a5oEwY7go-hha9L_7R5a6zT1QOy___J1p7gcoXKu1D8IoZ8kyR5ruT5IBNcsg9I0DYLq8rWx48YwBUUQnqtpzc7DMwpm4raqH81f8LBvMVN9qfIiD2bGq-QkCAmMp__1ffFP97tsr3cxZNgfpc7LDJymUw.2bREbvw2iFi-HmYF.rBozW2jZZOj20INwde6abnokid5GCT3jJsGU8EUOyreGZbhPDELqw-1upyVIoWfBjJGj65OhDBa8k0YV91KZQuSzCPLzwvgrfgp3RoO9wZ1hVM5fg8kCMnML2j7eQx2VwAmzUFmYCXDu8BqiCwYPQWVFxpy8MuE19gVFZtOgE3KjCsaYoBRgFnfbmEn2aCXbogVWxhrn8q_unV6M0iPfCU1mLmNZgHCo6OuzOn6WCWmJLffb7MZ0460Gb4m3R1bRPTzUVqO6Pnd4fjwI2sbixfLGt9QQhXlcocDR0H2-r1toLwY1WofWTqlbOSXpWwNNzX4qQkCL93z9QR33Ck-2yVPXBiAHtStnMTAVIpb-NUnBEbbcN0DCBW1TVyr3mx8dg6EHUrUvyAxBuJ9tSU_Z5HPMJvWRk-QR9B6Ftv-8HVXxlXulPcCM5Kxtfi1wO5iF2KQgyIawSZ-Agnsy_uWS0evjC8czzxStBS7tzIdERw882rBX9aIaZbpe1dt3MDtjyfP_L0B8rjQoo2W1VmP-cRJkVRq_JEsY9NqFaLfP66nRoaD7GgcatySh5QkfC4Ozygjf_sKEzHD3_9QdXrdoHK2rF3tWbaF-LwPAj1gtNFwVAsXg91j8phF181LKTxBSM-tAyTT4M3pxTGsLhyPkF2ALuTT-259e3kQBo_lQ0OjLo8HbsAA.jL5mnhiM4IGllxPlcVHsrQ'
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
        "guestLocationCountry": "NL",
        "arrivalDate": "2023-08-23",
        "departureDate": "2023-08-24",
        "numAdults": 1,
        "numChildren": 0,
        "numRooms": 1,
        "displayCurrency": None,
        "ctyhocn": "FRAHI",
        "language": "en",
        "guestId": None,
        "specialRates": {
            "aaa": False,
            "aarp": False,
            "governmentMilitary": False,
            "hhonors": True,
            "pnd": "",
            "senior": False,
            "teamMember": False,
            "owner": False,
            "ownerHGV": False,
            "familyAndFriends": False,
            "travelAgent": False,
            "smb": False,
            "specialOffer": False,
            "specialOfferName": None,
        },
        "pnd": None,
        "cacheId": "8ece214e-3fe0-47a0-8bb0-012f56fd25d7",
        "offerId": None,
        "knownGuest": True,
        "modifyingReservation": False,
        "currentlySelectedRoomTypeCode": None,
        "currentlySelectedRatePlanCode": None,
        "childAges": None,
        "adjoiningRoomStay": False,
    }
}

response = requests.post(url, json=query, headers=headers)

if response.status_code == 200:
    print("Success!")
    print(json.dumps(response.json(), indent=4))
else:
    print("Failed!")
    print(response.text)