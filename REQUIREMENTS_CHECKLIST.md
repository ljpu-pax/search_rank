# Requirements Checklist

## Core Requirements

### 1. Query Turbopuffer Collection ✅
- [x] Connect to Turbopuffer with correct API key
- [x] Use correct namespace: `search-test-v4`
- [x] Use correct region: `aws-us-west-2`
- [x] Query ~100K-200K user profiles
- [x] Handle 1024-dim embeddings (voyage-3)
- [x] Retrieve all relevant metadata fields

### 2. Re-rank Initial Hits (Optional) ✅
- [x] Implement cross-encoder re-ranking
- [x] Implement custom scoring with soft criteria
- [x] Implement hard criteria filtering
- [x] Use LTR features / rules-based approach

### 3. Evaluate via Live API ✅
- [x] POST to: `https://mercor-dev--search-eng-interview.modal.run/evaluate`
- [x] Use correct email in Authorization header
- [x] Submit config_path (.yml filename)
- [x] Submit object_ids (array of strings, max 10)
- [x] Ensure object_ids correspond to _id field
- [x] Submit in ranked/sorted order
- [x] Handle evaluation response

## Data Schema Understanding ✅

### Required Fields Being Used:
- [x] `_id` - Mongo ObjectId for submission
- [x] `vector` - 1024-dim embeddings
- [x] `rerankSummary` - Main text for matching
- [x] `deg_degrees` - For hard criteria (JD, MBA)
- [x] `deg_schools` - School names
- [x] `deg_fos` - Fields of study
- [x] `exp_titles` - Job titles
- [x] `exp_companies` - Company names
- [x] `exp_years` - Years of experience (bucketed: "1", "3", "5", "10")
- [x] `education` - Education array
- [x] `experience` - Experience array
- [x] `name` - Candidate name

### Understanding Field Formats:
- [x] Years buckets: "1", "3", "5", "10" (means 1+, 3+, 5+, 10+ years)
- [x] Experience format: `yrs_[bucket]::title_[title]::company_[company]::start_[year]::end_[year]`
- [x] Education format: `yrs_[bucket]::school_[school]::degree_[degree]::fos_[field]::start_[year]::end_[year]`
- [x] Degree types: bachelor's, master's, mba, jd, doctorate, certificate, high school, associate

## Query Requirements ✅

### Hard Criteria (Must-Haves):
- [x] Implement filtering for hard criteria
- [x] Prioritize hard criteria over soft criteria
- [x] Understand: "If these criteria aren't met, this person cannot be hired"

### Soft Criteria (Nice-to-Haves):
- [x] Implement scoring for soft criteria
- [x] Apply soft criteria AFTER hard criteria
- [x] Understand: Nice to have, but not dealbreakers

### Query Types:
- [x] Public queries tested (tax_lawyer.yml, bankers.yml)
- [ ] **IMPORTANT**: Private queries will test robustness
  - Note: 3 will mirror public set, 7 will test distribution shifts
  - System should generalize, not overfit to public queries

## Evaluation API Requirements ✅

### Headers:
- [x] Content-Type: application/json
- [x] Authorization: pujohn618@gmail.com (user's email)

### Request Body:
- [x] `config_path`: String (.yml filename)
- [x] `object_ids`: Array of strings
  - [x] Min 1, Max 10
  - [x] **IMPORTANT**: "Your private score submissions must include 10"
  - [x] Currently submitting 10 ✅

### Response Handling:
- [x] Parse evaluation metrics
- [x] Understand hard_scores (pass/fail with pass_rate)
- [x] Understand soft_scores (1-10 scale)
- [x] Understand final_score calculation

## Test Queries ✅

### Public Queries (Available):
- [x] Tax Lawyer query (tax_lawyer.yml)
  - [x] Natural language description
  - [x] Hard criteria defined
  - [x] Soft criteria defined
  - [x] Tested and evaluated
- [x] Banker query (bankers.yml)
  - [x] Natural language description
  - [x] Hard criteria defined
  - [x] Soft criteria defined
  - [x] Tested and evaluated

### Google Drive Link:
- [x] Accessed: `1BggMRCZ0BBRhrhOJWAQqE_3FPO85E7fMVKF3I1d_S0Q`
- [x] Retrieved query configurations

## API Keys ✅
- [x] TURBOPUFFER_API_KEY configured
- [x] VOYAGE_API_KEY configured
- [x] OAI_KEY configured (available but not used)

## Critical Submission Requirements ⚠️

### FOR FINAL PRIVATE EVALUATION:
- [ ] **MUST submit exactly 10 object_ids** (not 1-9)
- [x] Object IDs must be in ranked order (best first)
- [x] Use same email as assignment recipient
- [ ] **Test system on unseen queries** (will happen in interview)
- [ ] **Ensure robustness to distribution shifts**

## System Design Principles ✅

### Hard vs Soft Optimization:
- [x] "Build your system to first optimize for the hard criteria"
- [x] "Only then switch to thinking about soft criteria"
- [x] Current system: filters hard, then ranks by soft

### Generalization:
- ⚠️ "We will also have a private query set which you can't see"
- ⚠️ "3 queries will mirror public set, 7 are designed to test robustness to distribution shifts"
- [x] System uses generic keyword extraction (not query-specific)
- [x] Multi-field matching works across domains
- ⚠️ Should test more diverse query types if possible

## Missing/To Verify

### Potential Gaps:
1. ⚠️ **Private query testing** - Can't access until interview
   - Mitigation: System uses generic approach, not overfitted

2. ✅ **10 object_ids requirement** - CONFIRMED submitting 10
   - Tax lawyer: Submitting 10 ✅
   - Banker: Submitting 10 ✅

3. ⚠️ **Distribution shift robustness**
   - Only tested 2 query types (legal, finance)
   - Should we create synthetic queries to test?

4. ✅ **Email authorization** - Using pujohn618@gmail.com

5. ✅ **Turbopuffer Example Row** - Link provided but not critical
   - Already understanding schema through testing

## Recommendations

### Before Final Submission:
1. ✅ Verify all submissions use exactly 10 object_ids
2. ⚠️ Consider testing on more diverse synthetic queries
3. ✅ Ensure system doesn't overfit to tax_lawyer/banker patterns
4. ✅ Document approach for handling unseen query types
5. ✅ Verify email in .env matches assignment email

### System Strengths for Private Queries:
- ✅ Generic keyword extraction (not hardcoded)
- ✅ Multi-field scoring works across domains
- ✅ Hard criteria filtering is pattern-based
- ✅ Cross-encoder provides semantic understanding
- ✅ Demonstrated on 2 different domains (legal, finance)

## Status Summary

**COMPLETED**: ✅ All core requirements
**ATTENTION**: ⚠️ Private query robustness (can't test until interview)
**VERIFIED**: ✅ Submitting 10 object_ids as required
**READY**: ✅ System production-ready for evaluation
