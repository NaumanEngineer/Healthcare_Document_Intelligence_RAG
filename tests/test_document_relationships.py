from __future__ import annotations

import pytest

from src.retrieval.document_relationships import (
    DOCUMENT_RELATIONSHIPS,
    DocumentRelationship,
    get_related_document_ids,
    get_relationship_evidence_document_ids,
    get_relationships_for_document,
    list_document_relationships,
    validate_relationship_registry,
)


def test_registry_contains_expected_relationship():
    relationships = list_document_relationships()

    assert relationships == [
        {
            "source_document_id": "DOC-011",
            "relationship_type": "COMPLEMENTS",
            "target_document_id": "DOC-003",
            "evidence_document_id": "DOC-011",
        }
    ]


def test_outbound_complements_lookup():
    relationships = get_relationships_for_document(
        "DOC-011"
    )

    assert len(relationships) == 1

    relationship = relationships[0]

    assert (
        relationship["source_document_id"]
        == "DOC-011"
    )

    assert (
        relationship["target_document_id"]
        == "DOC-003"
    )

    assert (
        relationship["relationship_type"]
        == "COMPLEMENTS"
    )

    assert (
        relationship["related_document_id"]
        == "DOC-003"
    )

    assert (
        relationship["retrieval_direction"]
        == "OUTBOUND"
    )


def test_symmetric_complements_reverse_lookup():
    relationships = get_relationships_for_document(
        "DOC-003"
    )

    assert len(relationships) == 1

    relationship = relationships[0]

    assert (
        relationship["related_document_id"]
        == "DOC-011"
    )

    assert (
        relationship["retrieval_direction"]
        == "INBOUND_SYMMETRIC"
    )


def test_get_related_document_ids_outbound():
    assert get_related_document_ids(
        "DOC-011"
    ) == [
        "DOC-003"
    ]


def test_get_related_document_ids_reverse_symmetric():
    assert get_related_document_ids(
        "DOC-003"
    ) == [
        "DOC-011"
    ]


def test_relationship_type_filter_matches():
    assert get_related_document_ids(
        "DOC-011",
        relationship_type="COMPLEMENTS",
    ) == [
        "DOC-003"
    ]


def test_relationship_type_filter_normalises_case():
    assert get_related_document_ids(
        "DOC-011",
        relationship_type=" complements ",
    ) == [
        "DOC-003"
    ]


def test_relationship_type_filter_non_matching_returns_empty():
    assert get_related_document_ids(
        "DOC-011",
        relationship_type="CONFLICT",
    ) == []


def test_relationship_evidence_document_is_source_document():
    assert get_relationship_evidence_document_ids(
        "DOC-011"
    ) == [
        "DOC-011"
    ]


def test_relationship_evidence_document_available_from_reverse_lookup():
    assert get_relationship_evidence_document_ids(
        "DOC-003"
    ) == [
        "DOC-011"
    ]


def test_unknown_document_raises_key_error():
    with pytest.raises(KeyError):
        get_relationships_for_document(
            "DOC-999"
        )


def test_document_id_normalises_case_and_spaces():
    relationships = get_relationships_for_document(
        "  doc-011  "
    )

    assert len(relationships) == 1

    assert (
        relationships[0]["related_document_id"]
        == "DOC-003"
    )


def test_blank_document_id_rejected():
    with pytest.raises(ValueError):
        get_relationships_for_document(
            "   "
        )


def test_non_string_document_id_rejected():
    with pytest.raises(TypeError):
        get_relationships_for_document(
            123
        )


def test_invalid_relationship_type_rejected():
    with pytest.raises(ValueError):
        get_related_document_ids(
            "DOC-011",
            relationship_type="UNKNOWN",
        )


def test_non_string_relationship_type_rejected():
    with pytest.raises(TypeError):
        get_related_document_ids(
            "DOC-011",
            relationship_type=123,
        )


def test_self_relationship_rejected():
    with pytest.raises(ValueError):
        DocumentRelationship(
            source_document_id="DOC-011",
            relationship_type="COMPLEMENTS",
            target_document_id="DOC-011",
            evidence_document_id="DOC-011",
        )


def test_unregistered_source_rejected():
    with pytest.raises(ValueError):
        DocumentRelationship(
            source_document_id="DOC-999",
            relationship_type="COMPLEMENTS",
            target_document_id="DOC-003",
            evidence_document_id="DOC-011",
        )


def test_unregistered_target_rejected():
    with pytest.raises(ValueError):
        DocumentRelationship(
            source_document_id="DOC-011",
            relationship_type="COMPLEMENTS",
            target_document_id="DOC-999",
            evidence_document_id="DOC-011",
        )


def test_unregistered_evidence_document_rejected():
    with pytest.raises(ValueError):
        DocumentRelationship(
            source_document_id="DOC-011",
            relationship_type="COMPLEMENTS",
            target_document_id="DOC-003",
            evidence_document_id="DOC-999",
        )


def test_unsupported_relationship_type_rejected():
    with pytest.raises(ValueError):
        DocumentRelationship(
            source_document_id="DOC-011",
            relationship_type="RELATED_TO",
            target_document_id="DOC-003",
            evidence_document_id="DOC-011",
        )


def test_relationship_constructor_normalises_values():
    relationship = DocumentRelationship(
        source_document_id=" doc-011 ",
        relationship_type=" complements ",
        target_document_id=" doc-003 ",
        evidence_document_id=" doc-011 ",
    )

    assert (
        relationship.source_document_id
        == "DOC-011"
    )

    assert (
        relationship.relationship_type
        == "COMPLEMENTS"
    )

    assert (
        relationship.target_document_id
        == "DOC-003"
    )

    assert (
        relationship.evidence_document_id
        == "DOC-011"
    )


def test_duplicate_registry_edge_rejected():
    duplicate_edge = (
        DocumentRelationship(
            source_document_id="DOC-011",
            relationship_type="COMPLEMENTS",
            target_document_id="DOC-003",
            evidence_document_id="DOC-011",
        ),
        DocumentRelationship(
            source_document_id="DOC-011",
            relationship_type="COMPLEMENTS",
            target_document_id="DOC-003",
            evidence_document_id="DOC-011",
        ),
    )

    with pytest.raises(ValueError):
        validate_relationship_registry(
            duplicate_edge
        )


def test_registry_requires_tuple():
    with pytest.raises(TypeError):
        validate_relationship_registry(
            list(
                DOCUMENT_RELATIONSHIPS
            )
        )


def test_registry_rejects_non_relationship_item():
    with pytest.raises(TypeError):
        validate_relationship_registry(
            (
                "not-a-relationship",
            )
        )


def test_builtin_registry_validates():
    validate_relationship_registry(
        DOCUMENT_RELATIONSHIPS
    )


def test_to_dict_is_serialisable_shape():
    relationship = (
        DOCUMENT_RELATIONSHIPS[0]
    )

    assert relationship.to_dict() == {
        "source_document_id": "DOC-011",
        "relationship_type": "COMPLEMENTS",
        "target_document_id": "DOC-003",
        "evidence_document_id": "DOC-011",
    }
def test_active_only_excludes_relationship_when_target_not_active(
    monkeypatch,
):
    import src.retrieval.document_relationships as relationship_module

    temporary_relationships = (
        DocumentRelationship(
            source_document_id="DOC-011",
            relationship_type="COMPLEMENTS",
            target_document_id="DOC-014",
            evidence_document_id="DOC-011",
        ),
    )

    monkeypatch.setattr(
        relationship_module,
        "DOCUMENT_RELATIONSHIPS",
        temporary_relationships,
    )

    result = relationship_module.get_relationships_for_document(
        "DOC-011",
        active_only=True,
    )

    assert result == []


def test_active_only_false_allows_non_active_relationship_for_audit(
    monkeypatch,
):
    import src.retrieval.document_relationships as relationship_module

    temporary_relationships = (
        DocumentRelationship(
            source_document_id="DOC-011",
            relationship_type="COMPLEMENTS",
            target_document_id="DOC-014",
            evidence_document_id="DOC-011",
        ),
    )

    monkeypatch.setattr(
        relationship_module,
        "DOCUMENT_RELATIONSHIPS",
        temporary_relationships,
    )

    result = relationship_module.get_relationships_for_document(
        "DOC-011",
        active_only=False,
    )

    assert len(result) == 1

    assert (
        result[0]["related_document_id"]
        == "DOC-014"
    )


def test_related_document_ids_exclude_draft_when_active_only(
    monkeypatch,
):
    import src.retrieval.document_relationships as relationship_module

    temporary_relationships = (
        DocumentRelationship(
            source_document_id="DOC-011",
            relationship_type="COMPLEMENTS",
            target_document_id="DOC-014",
            evidence_document_id="DOC-011",
        ),
    )

    monkeypatch.setattr(
        relationship_module,
        "DOCUMENT_RELATIONSHIPS",
        temporary_relationships,
    )

    assert relationship_module.get_related_document_ids(
        "DOC-011",
        active_only=True,
    ) == []


def test_relationship_evidence_document_ids_respect_active_only(
    monkeypatch,
):
    import src.retrieval.document_relationships as relationship_module

    temporary_relationships = (
        DocumentRelationship(
            source_document_id="DOC-011",
            relationship_type="COMPLEMENTS",
            target_document_id="DOC-003",
            evidence_document_id="DOC-014",
        ),
    )

    monkeypatch.setattr(
        relationship_module,
        "DOCUMENT_RELATIONSHIPS",
        temporary_relationships,
    )

    assert (
        relationship_module.get_relationship_evidence_document_ids(
            "DOC-011",
            active_only=True,
        )
        == []
    )


def test_relationship_evidence_document_ids_allow_non_active_for_audit(
    monkeypatch,
):
    import src.retrieval.document_relationships as relationship_module

    temporary_relationships = (
        DocumentRelationship(
            source_document_id="DOC-011",
            relationship_type="COMPLEMENTS",
            target_document_id="DOC-003",
            evidence_document_id="DOC-014",
        ),
    )

    monkeypatch.setattr(
        relationship_module,
        "DOCUMENT_RELATIONSHIPS",
        temporary_relationships,
    )

    assert (
        relationship_module.get_relationship_evidence_document_ids(
            "DOC-011",
            active_only=False,
        )
        == [
            "DOC-014"
        ]
    )