from http import HTTPStatus
from rest_framework.response import Response
from api.serializers import ShortRecipeSerializer


class BaseRecipeAction:
    def handle_action(
            self, request, model, pk,
            err_msg_exist, err_msg_not_found
    ):
        user = request.user
        recipe = self.get_object()
        instance = model.objects.filter(user=user, recipe=recipe).first()

        if request.method == 'POST':
            if instance:
                return Response(
                    {'detail': err_msg_exist},
                    status=HTTPStatus.BAD_REQUEST,
                )

            model.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(recipe)
            return Response(
                serializer.data,
                status=HTTPStatus.CREATED,
            )

        if instance:
            instance.delete()
            return Response(status=HTTPStatus.NO_CONTENT)

        return Response(
            {'detail': err_msg_not_found},
            status=HTTPStatus.BAD_REQUEST,
        )
