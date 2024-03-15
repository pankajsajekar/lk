from django.http import Http404, JsonResponse
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from bson import json_util
import json
import datetime

from .models import neutron_collection, person_collection

class home(APIView):

    def get(self, request, *args, **kwargs):
        # person_collection.create_index([("$**", "text")])
        # search_query = "Sajekar"
        # personData = person_collection.find({ "$text": { "$search": search_query } })
        # return JsonResponse(personData, safe=False)
        return Response("hello")
    

# Search in this fields [DCID, Pincode, DC Name, City] and where that data matched that documents (records) will show
class SearchView2(APIView):
    def get(self, request, format=None):
        search_query = request.query_params.get('q', None)
        if search_query is None:
            return Response({"error": "Search term not provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            search_query = int(search_query)
        except ValueError:
            # If search_query cannot be converted to an integer, treat it as a string
            pass

        # Perform search using the provided search query
        cursor = neutron_collection.find({
            "$or": [
                {"DCID": search_query},
                {"Pincode": search_query},
                {"DC Name": {"$regex": search_query, "$options": "i"}},
                {"City": {"$regex": search_query, "$options": "i"}},
            ]
        })

        # Convert MongoDB cursor to list of dictionaries
        providerData = [json.loads(json_util.dumps(doc)) for doc in cursor]

        # Prepare serializer data
        serializer_data = {
            "status": "Successful",
            "data": providerData,
            "message": "Result Found Successfully",
            "serviceName": "searchService_Service",
            "timeStamp": datetime.datetime.now().isoformat(),
            "page": 1,
            "totalResult": len(providerData),
            "noOfResult": len(providerData),
            "code": status.HTTP_200_OK,
        }

        # Return the search results
        return Response(serializer_data)


class SearchDCView(APIView):
    def get(self, request, format=None):
        search_query = request.query_params.get('q', None)
        page_number = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 8))

        if search_query is None:
            return Response({"error": "Search term not provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Determine if the search query is an integer or a string
        try:
            search_query_int = int(search_query)
            search_query_str = None
        except ValueError:
            search_query_str = search_query
            search_query_int = None

        # Construct the query based on the type of the search query
        query = {}
        if search_query_int is not None:
            query["$or"] = [{"DCID": search_query_int}, {"Pincode": search_query_int}]
        elif search_query_str is not None:
            query["$or"] = [
                {"DC Name": {"$regex": search_query_str, "$options": "i"}},
                {"City": {"$regex": search_query_str, "$options": "i"}}
            ]

        # Perform search using the constructed query
        cursor = neutron_collection.find(query)
        
        # Convert MongoDB cursor to list of dictionaries
        # providerData = [json.loads(json_util.dumps(doc)) for doc in cursor]
        
        providerData = []
        for document in cursor:
            # Filter specific fields here
            filtered_data = {
                "DCID": document["DCID"],
                "DC Name": document["DC Name"],
                "Date of Empanelment": document["Date of Empanelment"],
                "Address": document["Address"],
                "State": document["State"],
                "City": document["City"],
                "Pincode": document["Pincode"],
                "E_Mail": document["E_Mail"],
                "Contact Person Name 1": document["Contact Person Name 1"],
                "Mobile number 1": document["Mobile number 1"],
            }
            providerData.append(filtered_data)

        # Get the total count of results
        total_results = len(providerData)

        # Calculate the total number of pages
        total_pages = (total_results + page_size - 1) // page_size

        # Paginate the results
        providerData = providerData[(page_number - 1) * page_size: page_number * page_size]

        # Prepare serializer data
        serializer_data = {
            "status": "Successful",
            "data": providerData,
            "message": "Result Found Successfully",
            "serviceName": "DCSearchService_Service",
            "timeStamp": datetime.datetime.now().isoformat(),
            "page": page_number,
            "totalPages": total_pages,
            "totalResult": total_results,
            "noOfResult": len(providerData),
            "code": status.HTTP_200_OK,
        }

        # Add previous and next URLs
        if page_number > 1:
            serializer_data["previous"] = request.build_absolute_uri(request.path_info + f"?q={search_query}&page={page_number - 1}&page_size={page_size}")
        if page_number < int(total_pages):
            serializer_data["next"] = request.build_absolute_uri(request.path_info + f"?q={search_query}&page={page_number + 1}&page_size={page_size}")

        # Return the search results
        return Response(serializer_data)


# Get Dc documents in Details
class DCView(APIView):
    def get(self, request, formate=None):
        dcID_query = int(request.query_params.get('dc', None))

        if dcID_query is None:
            return Response({"error": "DC Details not provided"}, status=status.HTTP_400_BAD_REQUEST)
         
        # count no of documents return 404
        dc_count = neutron_collection.count_documents({'DCID': dcID_query })
        if dc_count == 0:
            return Response({"error": "No DC Details found for the provided ID"}, status=status.HTTP_404_NOT_FOUND)
        
        dcDetail = neutron_collection.find({'DCID': dcID_query })
        dcDetailData = json.loads(json_util.dumps(dcDetail))

        serializer_data = {
            "status": "Success",
            "data": dcDetailData,
            "message": "DC Details Retrieved Successfully",
            "serviceName": "DCDetails_Service",
            "timeStamp": datetime.datetime.now().isoformat(),
            "code": status.HTTP_200_OK,
        }
        return Response(serializer_data)