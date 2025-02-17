from marshmallow import Schema, fields,validate
import uuid



class StudySchema(Schema):
    _id=fields.Str()
    studyTitle = fields.Str()
    studyStarted = fields.Str()
    studyEnded = fields.Str()
    studyStatus=fields.Bool()
    studyRespondents = fields.Str()
    studyKeywords = fields.List()
    studyData=fields.Dict()
    studyCreatedBy=fields.Dict()
    
    
    
    