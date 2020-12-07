import json


def storeAuditRecords(request, auditObj):
    try:
        records = request.get_data(as_text=True)
        records = json.loads(records)
        auditObj.insertMany(records)
        return '', 200
    except Exception as ex:
        return str(ex), 500
