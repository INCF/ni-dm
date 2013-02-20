---
layout: page
title: "NI-DM Draft Specification"
comments: true
sharing: true
footer: true
---

Purpose
-------

In this INCF Neuroimging Datasharing (NIDASH) Taskforce and BIRN derived data working group Request for Comments (INCF/BIRN RFC), we specify the NIDASH Data Model (NI-DM) Version 1.0 to enable the electronic exchange of information describing  human neuroimaging data, including provenance and related metadata. We define:

1. the core data model, a common computational representation and  
2. the vocabulary, a set of terms with associated data type information

The intent of this specification is to take the current [XCEDE](http://www.xcede.org), [XNAT](http://www.xnat.org) and other brain imaging schemas and represent metadata within the context of the [PROV data model](http://www.w3.org/TR/prov-dm/) (PROV-DM) being developed by the W3C and to ensure that all common metadata terms have proper definitions and data type information. By extending PROV-DM with common neuroimaging metadata, which we refer to as NI-DM types, we set up the environment to capture and exchange provenance information; leverage any [W3C](http://www.w3c.org) effort, resources or tools; and provide a consistent model that is easily extensible across potential future domains.

For every PROV element (entity, activity, agent, role, collection, bundle) described below, we describe a set of NI-DM types and their corresponding attributes. These are classified as required, recommended and optional to comply with existing and future databases.

Conventions
-----------
The following terms in italic and all-capital letters will be interpreted throughout this document as defined here.

REQUIRED:  
The Required attribute defines how strictly a Validation Tool will enforce the definition of a NI-DM type.   
- A given object must have data recorded for this data element.  
- All data must be valid values (i.e., adhere to all defined attributes).  

RECOMMENDED:  
These are metadata that would be useful to provide additional description of a given object.  
- Data is not required for every object.  
- All recorded data must be valid values (i.e., adhere to all defined attributes).  

OPTIONAL:    
Extensive metadata may be useful for future scientific work and this will require descriptions and a formal vocabulary that goes beyond the information that is stored in current databases or thought of in the current community.  
- Data is not required for every object.  
- Recorded data does not have to adhere to all defined attributes.  

