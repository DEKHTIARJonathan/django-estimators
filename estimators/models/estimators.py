# original based on sci-kit hashing function
from django.core.exceptions import ValidationError
from django.db import models
from estimators.models.base import HashableFileMixin


class Estimator(HashableFileMixin):

    """This class creates estimator objects that persists predictive models

        An Estimator instance has multiple attributes

            :description:
            :estimator:

            >>> from estimators.models import Estimator
            >>> est = Estimator()
            >>> est.estimator = object
            >>> est.description = "k-means with 5 clusters"
            >>> est.save()

        or

            >>> from estimators.models import Estimator
            >>> est = Estimator.get_or_create(object)
            >>> est.description = "kNN without parameter tuning"
            >>> est.save()
    """

    description = models.CharField(max_length=256)
    _estimator = None
    # required by base class, to refer to the estimator property
    _object_property_name = '_estimator'

    class Meta:
        db_table = 'estimators'

    def __repr__(self):
        return '<Estimator <Id %s> <Hash %s>: %s>' % (
            self.id, self.object_hash, self.estimator)

    @classmethod
    def get_by_estimator(cls, est):
        if est is not None:
            object_hash = cls._compute_hash(est)
        return cls.get_by_hash(object_hash)

    @property
    def estimator(self):
        """return the estimator, and load it into memory if it hasn't been loaded yet"""
        return self.get_object()

    @estimator.setter
    def estimator(self, obj):
        self.set_object(obj)

    def save(self, *args, **kwargs):
        self.full_clean(exclude=['description'])
        super().save(*args, **kwargs)

    def clean(self):
        if self.object_hash != self._compute_hash(self.estimator):
            raise ValidationError(
                "object_hash '%s' should be set by the estimator '%s'" %
                (self.object_hash, self.estimator))
        # if already persisted, do not update estimator
        obj = self.get_by_hash(self.object_hash)
        if self.id and self.object_hash != getattr(obj, 'object_hash', None):
            raise ValidationError(
                "Cannot persist updated estimator '%s'.  Create a new Estimator object." %
                self.estimator)
