import dictionary_util
from app.provider import db
from database.entities import User, Message

class UsersOverview:

    class Keys:
        SEARCH = "search"
        OFFSET = "offset"
        LIMIT = "limit"
        ONLY_CONTACTS = "only_contacts"
        USER_TYPE = "user_type"

    def __init__(self, identity_manager, request):
        self.identity_manager = identity_manager
        self.search = request.args.get(UsersOverview.Keys.SEARCH, default="")
        self.user_type = int(request.args.get(UsersOverview.Keys.USER_TYPE, default=-1))
        self.offset = int(request.args.get(UsersOverview.Keys.OFFSET, default=0))
        self.limit = int(request.args.get(UsersOverview.Keys.LIMIT, default=20))
        self.only_contacts = bool(request.args.get(UsersOverview.Keys.ONLY_CONTACTS, default=False))

    def apply_offset_and_limit(self, query):
        return query.offset(
            self.offset
        ).limit(
            self.limit
        )
    
    def apply_contacts_filter(self, query):
        if (self.only_contacts):
            my_user_id = self.identity_manager.user.server_id
            query = query.filter(
                User.server_id.in_(
                    db.session.query(
                        db.case(
                            [
                                (
                                    Message.sender_id == my_user_id,
                                    Message.receiver_id
                                )
                            ],
                            else_=Message.sender_id
                        )
                    ).filter(
                        db.or_(
                            Message.receiver_id == my_user_id,
                            Message.sender_id == my_user_id
                        )
                    ).subquery()
                )
            )
        return query
    
    def apply_type_filter(self, query):
        if (self.user_type != -1):
            query = query.filter(
                User.main_preference_mode == self.user_type
            )
        return query

    def apply_search_filter(self, query):
        if (len(self.search) > 0):
            search_query = "%{0}%".format(self.search)
            query = query.filter(
                db.or_(
                    User.lastname.ilike(
                        search_query
                    ),
                    User.firstname.ilike(
                        search_query
                    )
                )
                
            )
        return query
    
    def build(self):
        query = db.session.query(
            User
        ).options(
            db.noload(
                User.advertisements
            )
        )

        query = self.apply_contacts_filter(query)
        query = self.apply_type_filter(query)
        query = self.apply_search_filter(query)
        query = self.apply_offset_and_limit(query)

        users = query.all()
        return dictionary_util.dictionaries_from_objects(users)

        