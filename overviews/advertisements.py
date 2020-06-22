from app.provider import db
from database.entities import Advertisement, User, Category

class AdvertisementsOverview:

    class Keys:
        MAX_KM = "max_km"
        SEARCH = "search"
        CATS = "cats"
        OFFSET = "offset"
        LIMIT = "limit"
        ORDER = "order"
        SHOW_DELETED = "show_deleted"
        DISTANCE = "distance"

    def __init__(self, identity_manager, request):
        self.max_distance_km = int(request.args.get(AdvertisementsOverview.Keys.MAX_KM, default=10))
        self.search = request.args.get(AdvertisementsOverview.Keys.SEARCH, default="")
        cats_str = request.args.get(AdvertisementsOverview.Keys.CATS, default="")
        if (len(cats_str) > 0):
            self.cat_ids = list(map(int, cats_str.split(",")))
        else:
            self.cat_ids = []
        self.offset = int(request.args.get(AdvertisementsOverview.Keys.OFFSET, default=0))
        self.limit = int(request.args.get(AdvertisementsOverview.Keys.LIMIT, default=20))
        self.order = int(request.args.get(AdvertisementsOverview.Keys.ORDER, default=0))
        self.show_deleted = bool(request.args.get(AdvertisementsOverview.Keys.SHOW_DELETED, default=False))
        self.my_coord = identity_manager.user.coordinates

    def apply_deleted_filter(self, query):
        if not self.show_deleted:
            query = query.filter(
                Advertisement.deleted == False
            )
        return query
    
    def apply_search_filter(self, query):
        if (len(self.search) > 0):
            search_query = "%{0}%".format(self.search)
            query = query.filter(
                db.or_(
                    Advertisement.details.ilike(
                        search_query
                    ),
                    Advertisement.title.ilike(
                        search_query
                    )
                )
                
            )
        return query

    def apply_categories_filter(self, query):
        if len(self.cat_ids) > 0:
            query = query.filter(
                Advertisement.categories.any(
                    Category.server_id.in_(self.cat_ids)
                )
            )
        return query

    def apply_order(self, query):
        if (self.order == 0):
            query = query.order_by(
                Advertisement.distance(self.my_coord)
            )
        elif (self.order == 1):
            query = query.order_by(
                Advertisement.date_modified
            )
        elif (self.order == 2):
            query = query.order_by(
                Advertisement.date_added
            )
        return query
    
    def apply_offset_and_limit(self, query):
        return query.offset(
            self.offset
        ).limit(
            self.limit
        )
        

    def build(self):

        query = db.session.query(
            Advertisement,
            Advertisement.distance(self.my_coord)
        ).filter(
            Advertisement.distance(self.my_coord) < self.max_distance_km
        )

        query = self.apply_deleted_filter(query)
        query = self.apply_search_filter(query)
        query = self.apply_categories_filter(query)
        query = self.apply_order(query)
        query = self.apply_offset_and_limit(query)

        items = query.all()
        dictionaries = []
        for item in items:
            advertisement_dict = item[0].as_dict(
                ignored_columns=[
                    User.advertisements
                ]
            )
            distance = item[1]
            advertisement_dict[AdvertisementsOverview.Keys.DISTANCE] = distance
            dictionaries.append(advertisement_dict)

        return dictionaries