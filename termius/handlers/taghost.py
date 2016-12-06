# -*- coding: utf-8 -*-
"""Module with tag list command helpers."""
from ..core.exceptions import DoesNotExistException
from ..core.models.terminal import Tag, TagHost


class TagListArgs(object):
    """Helper for updating host tag list."""

    def __init__(self, command):
        """Create new tag list helper."""
        self.command = command
        self.storage = command.storage

    def update_taghosts(self, host, tag_instances):
        """Update binding for taghost."""
        current_taghost = self.storage.filter(
            TagHost, **{'host.id': host.id}
        )
        current_taghost_per_id = {i.tag.id: i for i in current_taghost}
        new_tag_per_id = {i.id: i for i in tag_instances}
        current_taghost_ids = set(current_taghost_per_id.keys())
        new_tag_ids = set(new_tag_per_id.keys())
        delete_taghosts = current_taghost_ids - new_tag_ids
        self.delete_outdated_taghost(
            [current_taghost_per_id[i] for i in delete_taghosts]
        )
        new_taghosts_ids = new_tag_ids - current_taghost_ids
        self.create_taghosts(
            host, [new_tag_per_id[i] for i in new_taghosts_ids]
        )

    def delete_outdated_taghost(self, delete_taghosts):
        """Delete tag host instance."""
        for i in delete_taghosts:
            self.storage.delete(i)

    def create_taghosts(self, host, tag_list):
        """Create new binding to host and to tag list."""
        taghost_list = [TagHost(host=host, tag=i) for i in tag_list]
        for i in taghost_list:
            self.storage.save(i)

    def get_or_create_tag_instances(self, tag_label_list):
        """Get tag list from list of tag label."""
        tags = [
            self.get_or_create_tag(i) for i in tag_label_list
        ]
        return tags

    def get_or_create_tag(self, tag_label):
        """Get or create new tag instance by tag_label."""
        try:
            return self.storage.get(Tag, **{'label': tag_label})
        except DoesNotExistException:
            return self.storage.create(Tag(label=tag_label))

    def get_tag_instances(self, tag_label_list):
        """Get tag list from list of tag label."""
        return self.storage.filter(Tag, **{'label.rcontains': tag_label_list})
