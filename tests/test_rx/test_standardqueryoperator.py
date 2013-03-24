from rx import Observable

class RxException(Exception):
    pass

def test_select_throws():
    def _raise(ex):
        raise RxException(ex)

    try:
        return Observable.returnvalue(1) \
            .select(lambda x, y: x) \
            .subscribe(lambda x: _raise("ex"))
    except RxException:
        pass

    try:
        return Observable.throw_exception('ex') \
               .select(lambda x, y: x) \
               .subscribe(on_error=lambda ex: _raise(ex))
    except RxException:
        pass

#     raises(function () {
#         return Observable.empty().select(function (x) {
#             return x;
#         }).subscribe(function (x) { }, function (ex) { }, function () {
#             throw 'ex';
#         });
#     });
#     return raises(function () {
#         return Observable.create(function (o) {
#             throw 'ex';
#         }).select(function (x) {
#             return x;
#         }).subscribe();
#     });

# });