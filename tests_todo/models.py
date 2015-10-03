import unittest

from django.conf import settings
from django.contrib.auth.models import get_user_model
from django.db import models as dj_models
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError

from pytoolbox.django.models import fields, mixins


class Keyword(mixins.BetterUniquenessErrorsMixin, dj_models.Model):

    created_by = fields.CreatedByField()
    label = fields.CharField(max_length=50)

    class Meta:
        unique_together = (('created_by', 'parent'), )


class Node(mixins.AutoUpdateFieldsMixin, dj_models.Model):

    created_by = fields.CreatedByField()
    parent = dj_models.ForeignKey('self', null=True, related_name='child_set')
    keyword_set = dj_models.ManyToManyField(Keyword, null=True)
    metadata = dj_models.JSONField()


class Profile(mixins.AutoUpdateFieldsMixin, dj_models.Model):

    user = dj_models.OneToOneField(settings.AUTH_USER_MODEL)


class AutoUpdateFieldsMixinTestCase(object):

    tags = ('django', 'models')

    def setUp(self):
        super().setUp()
        self.node = Node(created_by=self.user)
        self.set_equal(self.node._setted_fields, set())
        self.node.save()

    def test_foreign_key(self):
        parent = Node.objects.create(created_by=self.user)
        self.node.parent = parent
        self.set_equal(self.node._setted_fields, {'parent_id'})
        self.set_equal(parent._setted_fields, set())
        self.node.save()
        self.equal(self.node.reload().parent, parent)
        parent.child_set = []
        self.set_equal(parent._setted_fields, set())
        parent.save()
        self.is_none(self.node.reload().parent)

    def test_immutable_and_reset(self):
        self.node.title = 'New Title'
        self.set_equal(self.node._setted_fields, {'title'})
        self.node.save()
        self.equal(self.node.reload().title, 'New Title')
        self.set_equal(self.node._setted_fields, set())

    def test_many_to_many(self):
        keyword_set = [Keyword.objects.create(created_by=self.user, label=str(i)) for i in range(2)]
        self.node.keyword_set = keyword_set
        self.set_equal(self.node._setted_fields, set())
        self.node.save()
        self.set_equal(set(self.node.keyword_set.all()), set(keyword_set))
        self.set_equal(self.node._setted_fields, set())
        self.node.keyword_set = {keyword_set[0]}
        self.set_equal(self.node._setted_fields, set())
        self.node.save()
        self.set_equal(set(self.node.keyword_set.all()), {keyword_set[0]})

    def test_mutable(self):
        self.node.metadata = metadata = {'this': ['is', 'a', {'nested': 'mutable'}]}
        self.set_equal(self.node._setted_fields, {'metadata'})
        self.node.save()
        self.equal(self.node.reload().metadata, metadata)
        metadata['this'][-1] = {'new': 'value'}
        self.set_equal(self.node._setted_fields, set())
        self.node.metadata = metadata
        self.set_equal(self.node._setted_fields, {'metadata'})
        self.node.save()
        self.dict_equal(self.node.reload().metadata, metadata)

    def test_required_one_to_one(self):
        profile = Profile()
        profile.user = self.user
        self.set_equal(profile._setted_fields, set())
        profile.save()
        profile.user = new_user = get_user_model().objects.create()
        self.set_equal(profile._setted_fields, {'user_id'})
        profile.save()
        self.equal(profile.reload().user, new_user)


class BetterUniquenessErrorsMixinModelTestCase(object):

    tags = ('django', 'models')

    def setUp(self):
        super().setUp()
        keyword = Keyword.objects.create(created_by=self.user, label='City')
        keyword.validate_unique()
        self.keyword = Keyword(created_by=self.user, label='City')

    def assertExceptionCodesByField(self, exception, expected):
        self.assertDictEqual({k: [e.code for e in v] for k, v in exception.error_dict.items()}, expected)

    def test_perform_unique_checks(self):
        with self.raises(ValidationError) as a:
            self.keyword.validate_unique()
        self.exception_codes_by_field(a.exception, {'label': ['unique']})
        self.keyword.unique_together_hide_fields = ()
        with self.raises(ValidationError) as a:
            self.keyword.validate_unique()
        self.exception_codes_by_field(a.exception, {NON_FIELD_ERRORS: ['unique_together']})

    @unittest.mock.patch(
        'pytoolbox.django.models.mixins.BetterUniquenessErrorsMixin._handle_hidden_duplicate_key_error'
    )
    def test_save_map_to_0_fields(self, handler):
        self.keyword.unique_together_hide_fields = ('created_by', 'label')
        self.keyword.save()
        handler.assert_called_once()

    def test_save_map_to_1_field(self):
        with self.raises(ValidationError) as a:
            self.keyword.save()
        self.exception_codes_by_field(a.exception, {'label': ['unique']})

    def test_save_map_to_multiple_fields(self):
        self.keyword.unique_together_hide_fields = ()
        with self.raises(ValidationError) as a:
            self.keyword.save()
        self.equal(a.exception.params['unique_check'], ['created_by', 'label'])
