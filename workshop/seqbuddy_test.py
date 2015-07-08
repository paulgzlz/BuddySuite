#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# NOTE: BioPython 16.6+ required.

import pytest
from hashlib import md5
from Bio import SeqIO
import os
import subprocess
import re
from copy import deepcopy
from Bio.Alphabet import IUPAC

try:
    import workshop.SeqBuddy as Sb
except ImportError:
    import SeqBuddy as Sb
import MyFuncs

write_file = MyFuncs.TempFile()


def seqs_to_hash(_seqbuddy, mode='hash'):
    if _seqbuddy.out_format in ["gb", "genbank"]:
            for _rec in _seqbuddy.records:
                try:
                    if re.search("(\. )+", _rec.annotations['organism']):
                        _rec.annotations['organism'] = "."
                except KeyError:
                    pass

    if _seqbuddy.out_format == "phylipi":
        write_file.write(Sb.phylipi(_seqbuddy, "relaxed"))
    elif _seqbuddy.out_format == "phylipis":
        write_file.write(Sb.phylipi(_seqbuddy, "strict"))
    else:
        _seqbuddy.write(write_file.path)

    seqs_string = "{0}\n".format(write_file.read().strip())

    if mode != "hash":
        return seqs_string

    _hash = md5(seqs_string.encode()).hexdigest()
    return _hash


root_dir = os.getcwd()


def resource(file_name):
    return "{0}/unit_test_resources/{1}".format(root_dir, file_name)


seq_files = ["Mnemiopsis/Mnemiopsis_cds.fa", "Mnemiopsis/Mnemiopsis_cds.gb", "Mnemiopsis/Mnemiopsis_cds.nex",
             "Mnemiopsis/Mnemiopsis_cds.phy", "Mnemiopsis/Mnemiopsis_cds.phyr", "Mnemiopsis/Mnemiopsis_cds.stklm",
             "Mnemiopsis/Mnemiopsis_pep.fa", "Mnemiopsis/Mnemiopsis_pep.gb", "Mnemiopsis/Mnemiopsis_pep.nex",
             "Mnemiopsis/Mnemiopsis_pep.phy", "Mnemiopsis/Mnemiopsis_pep.phyr", "Mnemiopsis/Mnemiopsis_pep.stklm"]


@pytest.mark.parametrize("seq_file", seq_files)
def test_instantiate_seqbuddy_from_file(seq_file):
    assert type(Sb.SeqBuddy(resource(seq_file))) == Sb.SeqBuddy


@pytest.mark.parametrize("seq_file", seq_files)
def test_instantiate_seqbuddy_from_handle(seq_file):
    with open(resource(seq_file), 'r') as ifile:
        assert type(Sb.SeqBuddy(ifile)) == Sb.SeqBuddy


@pytest.mark.parametrize("seq_file", seq_files)
def test_instantiate_seqbuddy_from_raw(seq_file):
    with open(resource(seq_file), 'r') as ifile:
        assert type(Sb.SeqBuddy(ifile.read())) == Sb.SeqBuddy


# Now that we know that all the files are being turned into SeqBuddy objects okay, make them all objects so it doesn't
# need to be done over and over for each subsequent test.
def set_sb_objs():
    return [Sb.SeqBuddy(resource(x)) for x in seq_files]
sb_objects = set_sb_objs()

# formats = ["fasta", "gb", "nexus", "phylip", "phylip-relaxed", "stockholm"]

# ######################  'uc', '--uppercase' ###################### #
hashes = ["25073539df4a982b7f99c72dd280bb8f", "2e02a8e079267bd9add3c39f759b252c", "52e74a09c305d031fc5263d1751e265d",
          "7117732590f776836cbabdda05f9a982", "3d17ebd1f6edd528a153ea48dc37ce7d", "b82538a4630810c004dc8a4c2d5165ce",
          "c10d136c93f41db280933d5b3468f187", "7a8e25892dada7eb45e48852cbb6b63d", "8b6737fe33058121fd99d2deee2f9a76",
          "40f10dc94d85b32155af7446e6402dea", "b229db9c07ff3e4bc049cea73d3ebe2c", "f35cbc6e929c51481e4ec31e95671638"]
hashes = [(sb_objects[indx], value) for indx, value in enumerate(hashes)]


@pytest.mark.parametrize("seqbuddy,next_hash", hashes)
def test_uppercase(seqbuddy, next_hash):  # NOTE: Biopython always writes genbank to spec in lower case
    tester = Sb.uppercase(seqbuddy)
    assert seqs_to_hash(tester) == next_hash

# ######################  'lc', '--lowercase' ###################### #
hashes = ["b831e901d8b6b1ba52bad797bad92d14", "2e02a8e079267bd9add3c39f759b252c", "cb1169c2dd357771a97a02ae2160935d",
          "d1524a20ef968d53a41957d696bfe7ad", "99d522e8f52e753b4202b1c162197459", "228e36a30e8433e4ee2cd78c3290fa6b",
          "14227e77440e75dd3fbec477f6fd8bdc", "7a8e25892dada7eb45e48852cbb6b63d", "17ff1b919cac899c5f918ce8d71904f6",
          "c934f744c4dac95a7544f9a814c3c22a", "6a3ee818e2711995c95372afe073490b", "c0dce60745515b31a27de1f919083fe9"]
hashes = [(sb_objects[indx], value) for indx, value in enumerate(hashes)]


@pytest.mark.parametrize("seqbuddy,next_hash", hashes)
def test_lowercase(seqbuddy, next_hash):
    # We know uppercase works, so convert objects to uppercase before testing lowercase function
    seqbuddy = Sb.uppercase(seqbuddy)
    tester = Sb.lowercase(seqbuddy)
    assert seqs_to_hash(tester) == next_hash

# ######################  '-ofa', '--order_features_alphabetically' ###################### #
hashes = ["b831e901d8b6b1ba52bad797bad92d14", "21547b4b35e49fa37e5c5b858808befb", "cb1169c2dd357771a97a02ae2160935d",
          "d1524a20ef968d53a41957d696bfe7ad", "99d522e8f52e753b4202b1c162197459", "228e36a30e8433e4ee2cd78c3290fa6b",
          "14227e77440e75dd3fbec477f6fd8bdc", "d0297078b4c480a49b6da5b719310d0e", "17ff1b919cac899c5f918ce8d71904f6",
          "c934f744c4dac95a7544f9a814c3c22a", "6a3ee818e2711995c95372afe073490b", "c0dce60745515b31a27de1f919083fe9"]

hashes = [(sb_objects[indx], value) for indx, value in enumerate(hashes)]


@pytest.mark.parametrize("seqbuddy,next_hash", hashes)  # modifies in place?
def test_order_features_alphabetically(seqbuddy, next_hash):
    tester = Sb.order_features_alphabetically(seqbuddy)
    assert seqs_to_hash(tester) == next_hash

# ######################  '-mw', '--molecular_weight' ###################### # ToDo: review
mw_files = ["mw/mw_test_pep.fa", "mw/mw_test_cds_a.fa", "mw/mw_test_cds_u.fa", "mw/mw_test_rna_a.fa",
            "mw/mw_test_rna_u.fa"]
mw_formats = ["protein", "dna", "dna", "rna", "rna"]
mw_objects = [(Sb.SeqBuddy(resource(value), "fasta", "fasta", mw_formats[indx])) for indx, value in enumerate(mw_files)]
expected_mw = [[2505.75, None], [5022.19, 10044.28], [3168.0, 6335.9], [4973.0, None], [3405.0, None]]
expected_mw = [(mw_objects[indx], value) for indx, value in enumerate(expected_mw)]


@pytest.mark.parametrize("seqbuddy,next_mw", expected_mw)
def test_molecular_weight(seqbuddy, next_mw):
    tester = Sb.molecular_weight(seqbuddy)
    masses_ss = tester['masses_ss']
    masses_ds = tester['masses_ds']
    assert masses_ss[0] == next_mw[0]
    if len(masses_ds) != 0:
        assert masses_ds[0] == next_mw[1]

# ######################  'cs', '--clean_seq' ###################### # ToDo: review
cs_files = ["cs/cs_test_pep.fa", "cs/cs_test_cds_a.fa", "cs/cs_test_cds_u.fa"]
cs_formats = ["protein", "dna", "dna"]
cs_objects = [(Sb.SeqBuddy(resource(value), "fasta", "fasta", cs_formats[indx])) for indx, value in enumerate(cs_files)]
cs_hashes = ['9289d387b1c8f990b44a9cb15e12443b', "8e161d5e4115bf483f5196adf7de88f0", "2e873cee6f807fe17cb0ff9437d698fb"]
cs_hashes = [(cs_objects[indx], value) for indx, value in enumerate(cs_hashes)]


@pytest.mark.parametrize("seqbuddy,next_hash", cs_hashes)
def test_clean_seq(seqbuddy, next_hash):
    tester = Sb.clean_seq(seqbuddy)
    assert seqs_to_hash(tester) == next_hash

# ######################  'dm', '--delete_metadata' ###################### #
hashes = ["aa92396a9bb736ae6a669bdeaee36038", "544ab887248a398d6dd1aab513bae5b1", "cb1169c2dd357771a97a02ae2160935d",
          "d1524a20ef968d53a41957d696bfe7ad", "99d522e8f52e753b4202b1c162197459", "a50943ccd028b6f5fa658178fa8cf54d",
          "bac5dc724b1fee092efccd2845ff2513", "858e8475f7bc6e6a24681083a8635ef9", "17ff1b919cac899c5f918ce8d71904f6",
          "c934f744c4dac95a7544f9a814c3c22a", "6a3ee818e2711995c95372afe073490b", "e224c16f6c27267b5f104c827e78df33"]
hashes = [(sb_objects[indx], value) for indx, value in enumerate(hashes)]


@pytest.mark.parametrize("seqbuddy,next_hash", hashes)
def test_delete_metadata(seqbuddy, next_hash):
    tester = Sb.delete_metadata(seqbuddy)
    assert seqs_to_hash(tester) == next_hash

# ######################  'rs', '--raw_seq' ###################### #
hashes = ["6f0ff2d43706380d92817e644e5b78a5", "6f0ff2d43706380d92817e644e5b78a5", "6f0ff2d43706380d92817e644e5b78a5",
          "cda59127d6598f44982a2d1875064bb1", "6f0ff2d43706380d92817e644e5b78a5", "6f0ff2d43706380d92817e644e5b78a5",
          "cdfe71aefecc62c5f5f2f45e9800922c", "cdfe71aefecc62c5f5f2f45e9800922c", "cdfe71aefecc62c5f5f2f45e9800922c",
          "3f48f81ab579a389947641f36889901a", "cdfe71aefecc62c5f5f2f45e9800922c", "cdfe71aefecc62c5f5f2f45e9800922c"]
hashes = [(sb_objects[indx], value) for indx, value in enumerate(hashes)]


@pytest.mark.parametrize("seqbuddy,next_hash", hashes)
def test_raw_seq(seqbuddy, next_hash):
    tester = Sb.raw_seq(seqbuddy)
    tester = md5(tester.encode()).hexdigest()
    assert tester == next_hash

# ######################  'tr', '--translate' ###################### #
sb_objects = set_sb_objs()
hashes = ["3de7b7be2f2b92cf166b758625a1f316", "c841658e657b4b21b17e4613ac27ea0e", ]
# NOTE: the first 6 sb_objects are DNA.
hashes = [(sb_objects[indx], value) for indx, value in enumerate(hashes)]


@pytest.mark.parametrize("seqbuddy,next_hash", hashes)
def test_translate(seqbuddy, next_hash):
    tester = Sb.translate_cds(seqbuddy)
    assert seqs_to_hash(tester) == next_hash


def test_translate_pep_exception():
    with pytest.raises(TypeError):
        Sb.translate_cds(sb_objects[6])

# ######################  'sfr', '--select_frame' ###################### #
# Only fasta
sb_objects = set_sb_objs()
hashes = ["b831e901d8b6b1ba52bad797bad92d14", "a518e331fb29e8be0fdd5f3f815f5abb", "2cbe39bea876030da6d6bd45e514ae0e"]
frame = [1, 2, 3]
hashes = [(deepcopy(sb_objects[0]), _hash, frame[indx]) for indx, _hash in enumerate(hashes)]


@pytest.mark.parametrize("seqbuddy,next_hash,shift", hashes)
def test_select_frame(seqbuddy, next_hash, shift):
    tester = Sb.select_frame(seqbuddy, shift)
    assert seqs_to_hash(tester) == next_hash


def test_select_frame_pep_exception():
    with pytest.raises(TypeError):  # If protein is input
        Sb.select_frame(sb_objects[6], 2)

# ######################  'tr6', '--translate6frames' ###################### #
# Only fasta and genbank
hashes = ["d5d39ae9212397f491f70d6928047341", "42bb6caf86d2d8be8ab0defabc5af477"]
hashes = [(deepcopy(sb_objects[indx]), value) for indx, value in enumerate(hashes)]


@pytest.mark.parametrize("seqbuddy,next_hash", hashes)
def test_translate6frames(seqbuddy, next_hash):
    tester = Sb.translate6frames(seqbuddy)
    assert seqs_to_hash(tester) == next_hash


def test_translate6frames_pep_exception():
    with pytest.raises(TypeError):
        Sb.translate6frames(sb_objects[6])

# ######################  'btr', '--back_translate' ###################### #
# Only fasta and genbank
hashes = ["1b14489a78bfe8255c777138877b9648", "b6bcb4e5104cb202db0ec4c9fc2eaed2",
          "859ecfb88095f51bfaee6a1d1abeb50f", "ba5c286b79a3514fba0b960ff81af25b",
          "952a91a4506afb57f27136aa1f2a8af9", "40c4a3e08c811b6bf3be8bedcb5d65a0"]
organisms = ['human', 'human', 'yeast', 'yeast', 'ecoli', 'ecoli']
hashes = [(deepcopy(sb_objects[sb_obj_indx]), organisms[indx], hashes[indx]) for indx, sb_obj_indx in
          enumerate([6, 7, 6, 7, 6, 7])]

@pytest.mark.parametrize("seqbuddy,_organism,next_hash", hashes)
def test_back_translate(seqbuddy, _organism, next_hash):
    seqbuddy.alpha = IUPAC.protein
    tester = Sb.back_translate(seqbuddy, 'OPTIMIZED', _organism)
    assert seqs_to_hash(tester) == next_hash


def test_back_translate_nucleotide_exception():
    with pytest.raises(TypeError):
        Sb.back_translate(sb_objects[1])

# ######################  'd2r', '--transcribe' ###################### #
hashes = ["d2db9b02485e80323c487c1dd6f1425b", "9ef3a2311a80f05f21b289ff7f401fff",
          "f3bd73151645359af5db50d2bdb6a33d", "1371b536e41e3bca304794512122cf17",
          "866aeaca326891b9ebe5dc9d762cba2c", "45b511f34653e3b984e412182edee3ca"]
hashes = [(sb_objects[indx], value) for indx, value in enumerate(hashes)]


@pytest.mark.parametrize("seqbuddy,next_hash", hashes)
def test_transcribe(seqbuddy, next_hash):
    tester = Sb.dna2rna(seqbuddy)
    assert seqs_to_hash(tester) == next_hash


def test_transcribe_pep_exception():  # Asserts that a ValueError will be thrown if user inputs protein
    with pytest.raises(TypeError):
        Sb.dna2rna(sb_objects[6])

# ######################  'r2d', '--back_transcribe' ###################### #
# NOTE: The sb_objects were converted to RNA in the previous test
hashes = ["b831e901d8b6b1ba52bad797bad92d14", "2e02a8e079267bd9add3c39f759b252c",
          "cb1169c2dd357771a97a02ae2160935d", "d1524a20ef968d53a41957d696bfe7ad",
          "99d522e8f52e753b4202b1c162197459", "228e36a30e8433e4ee2cd78c3290fa6b"]
hashes = [(sb_objects[indx], value) for indx, value in enumerate(hashes)]

@pytest.mark.parametrize("seqbuddy,next_hash", hashes)
def test_back_transcribe(seqbuddy, next_hash):
    tester = Sb.rna2dna(seqbuddy)
    assert seqs_to_hash(tester) == next_hash


def test_back_transcribe_pep_exception():  # Asserts that a TypeError will be thrown if user inputs protein
    with pytest.raises(TypeError):
        Sb.rna2dna(sb_objects[6])

# ######################  'cmp', '--complement' ###################### #
hashes = ["e4a358ca57aca0bbd220dc6c04c88795", "3366fcc6ead8f1bba4a3650e21db4ec3",
          "365bf5d08657fc553315aa9a7f764286", "10ce87a53aeb5bd4f911380ebf8e7a85",
          "8e5995813da43c7c00e98d15ea466d1a", "5891348e8659290c2355fabd0f3ba4f4"]
hashes = [(deepcopy(sb_objects[indx]), value) for indx, value in enumerate(hashes)]


@pytest.mark.parametrize("seqbuddy,next_hash", hashes)
def test_complement(seqbuddy, next_hash):
    tester = Sb.complement(seqbuddy)
    assert seqs_to_hash(tester) == next_hash


def test_complement_pep_exception():  # Asserts that a TypeError will be thrown if user inputs protein
    with pytest.raises(TypeError):
        Sb.complement(sb_objects[6])

# ######################  'rc', '--reverse_complement' ###################### #
hashes = ["e77be24b8a7067ed54f06e0db893ce27", "47941614adfcc5bd107f71abef8b3e00", "f549c8dc076f6b3b4cf5a1bc47bf269d",
          "a62edd414978f91f7391a59fc1a72372", "08342be5632619fd1b1251b7ad2b2c84", "0d6b7deda824b4fc42b65cb87e1d4d14"]
hashes = [(deepcopy(sb_objects[indx]), value) for indx, value in enumerate(hashes)]


@pytest.mark.parametrize("seqbuddy,next_hash", hashes)
def test_reverse_complement(seqbuddy, next_hash):
    tester = Sb.reverse_complement(seqbuddy)
    assert seqs_to_hash(tester) == next_hash


def test_reverse_complement_pep_exception():  # Asserts that a TypeError will be thrown if user inputs protein
    with pytest.raises(TypeError):
        Sb.reverse_complement(sb_objects[6])

# ######################  'li', '--list_ids' ###################### #
# first test that 1 column works for all file types
hashes = ["1c4a395d8aa3496d990c611c3b6c4d0a", "1c4a395d8aa3496d990c611c3b6c4d0a", "1c4a395d8aa3496d990c611c3b6c4d0a",
          "78a9289ab2d508a13c76cf9f5a308cc5", "1c4a395d8aa3496d990c611c3b6c4d0a", "1c4a395d8aa3496d990c611c3b6c4d0a"]
hashes = [(sb_objects[indx], value) for indx, value in enumerate(hashes)]


@pytest.mark.parametrize("seqbuddy,next_hash", hashes)
def test_list_ids_one_col(seqbuddy, next_hash):
    tester = Sb.list_ids(seqbuddy, 1)
    tester = md5(tester.encode()).hexdigest()
    assert tester == next_hash

# Now test different numbers of columns
hashes = ["6fcee2c407bc4f7f70e0ae2a7e101761", "1c4a395d8aa3496d990c611c3b6c4d0a", "6fcee2c407bc4f7f70e0ae2a7e101761",
          "bd177e4db7dd772c5c42199b0dff49a5", "6b595a436a38e353a03e36a9af4ba1f9", "c57028374ed3fc474009e890acfb041e"]
columns = [-2, 0, 2, 5, 10, 100]
hashes = [(sb_objects[0], value, columns[indx]) for indx, value in enumerate(hashes)]


@pytest.mark.parametrize("seqbuddy,next_hash,cols", hashes)
def test_list_ids_multi_col(seqbuddy, next_hash, cols):
    tester = Sb.list_ids(seqbuddy, cols)
    tester = md5(tester.encode()).hexdigest()
    assert tester == next_hash

#  are num_seqs and ave_seq_length even worth testing? YES!!!! Just feed in numbers though, no need to calculate hashes

# ######################  'cts', '--concat_seqs' ###################### #
hashes = ["2e46edb78e60a832a473397ebec3d187", "7421c27be7b41aeedea73ff41869ac47",
          "494988ffae2ef3072c1619eca8a0ff3b", "710cad348c5560446daf2c916ff3b3e4",
          "494988ffae2ef3072c1619eca8a0ff3b", "494988ffae2ef3072c1619eca8a0ff3b",
          "46741638cdf7abdf53c55f79738ee620", "8d0bb4e5004fb6a1a0261c30415746b5",
          "2651271d7668081cde8012db4f9a6574", "36526b8e0360e259d8957fa2261cf45a",
          "2651271d7668081cde8012db4f9a6574", "2651271d7668081cde8012db4f9a6574"]
hashes = [(sb_objects[indx], value) for indx, value in enumerate(hashes)]


@pytest.mark.parametrize("seqbuddy,next_hash", hashes)
def test_concat_seqs(seqbuddy, next_hash):
    tester = Sb.concat_seqs(seqbuddy)
    assert seqs_to_hash(tester) == next_hash

# ToDo: Test the _clean parameter

# ######################  'fd2p', '--map_features_dna2prot' ###################### #
# Map the genbank DNA file to all protein files, and the fasta DNA file to fasta protein
#sb_objects = set_sb_objs()
hashes = ["5216ef85afec36d5282578458a41169a", "a8f7c129cf57a746c20198bf0a6b9cf4", "0deeea532d6dcbc0486e9b74d0d6aca8",
          "d595fabb157d5c996357b6a7058af4e8", "bb06e94456f99efc2068f5a52f0e0462", "a287e0054df7f5df76e792e0e0ab6756"]
prot_indx = [6, 7, 8, 9, 10, 11]
hashes = [(deepcopy(sb_objects[1]), deepcopy(sb_objects[prot_indx[indx]]), value) for indx, value in enumerate(hashes)]
hashes.append((deepcopy(sb_objects[0]), deepcopy(sb_objects[6]), "854566b485af0f277294bbfb15f7dd0a"))

@pytest.mark.parametrize("_dna,_prot,next_hash", hashes)
def test_map_features_dna2prot(_dna, _prot, next_hash):
    _prot.alpha = IUPAC.protein
    _dna.alpha = IUPAC.ambiguous_dna
    tester = Sb.map_features_dna2prot(_dna, _prot)
    assert seqs_to_hash(tester) == next_hash

"""
# 'fp2d', '--map_features_prot2dna'
fp2d_hashes = ["f320b57dbf05517cba5bcc2e5ef36781", "57b12348267157870c83e85e3f0a5941",
               "f320b57dbf05517cba5bcc2e5ef36781", "064431b9e108595e13a0b5cf3fada88a",
               "f320b57dbf05517cba5bcc2e5ef36781", "f320b57dbf05517cba5bcc2e5ef36781",
               "9c6fb895e4c810bfdacdab3befe0882c", "604eaa62a8a71dbad31348ee8db03274",
               "9c6fb895e4c810bfdacdab3befe0882c", "cf0d0ce76aa7d268cca2aa2afe71fcc1",
               "9c6fb895e4c810bfdacdab3befe0882c", "9c6fb895e4c810bfdacdab3befe0882c",
               "d64eb777d4ba1c64397cb7bf089b2945", "c550801b2f8f87bcd973a55dd30130a0",
               "d64eb777d4ba1c64397cb7bf089b2945", "d373cac8c896a5379e3c0b6c767526db",
               "d64eb777d4ba1c64397cb7bf089b2945", "d64eb777d4ba1c64397cb7bf089b2945",
               "a49f248f982547fa1143cc711bb0eae7", "ac103e7d6ba14b92f6c52cf11666219f",
               "a49f248f982547fa1143cc711bb0eae7", "a49f248f982547fa1143cc711bb0eae7",
               "a49f248f982547fa1143cc711bb0eae7", "a49f248f982547fa1143cc711bb0eae7",
               "ddecbbc1a905b43e57085117ecd5773e", "4a5bc89b11c99eeb5a35a363384ccf14",
               "ddecbbc1a905b43e57085117ecd5773e", "a49f248f982547fa1143cc711bb0eae7",
               "ddecbbc1a905b43e57085117ecd5773e", "ddecbbc1a905b43e57085117ecd5773e",
               "1bf626401ac805e3d53e8ffe3d8350e9", "dffde8d5a130291e288d6268cf152d3a",
               "1bf626401ac805e3d53e8ffe3d8350e9", "5228ca449ce6a25fddf02cd230472146",
               "1bf626401ac805e3d53e8ffe3d8350e9", "1bf626401ac805e3d53e8ffe3d8350e9"]
fp2d_objects = []
hash_indx = 0
for dna in seq_files[:6]:
    for prot in seq_files[6:]:
        fp2d_objects.append((prot, dna, fp2d_hashes[hash_indx]))
        hash_indx += 1


@pytest.mark.parametrize("_prot,_dna,next_hash", fp2d_objects)
def test_map_features_prot2dna(_prot, _dna, next_hash):
    _dna = Sb.SeqBuddy(resource(_dna))
    _prot = Sb.SeqBuddy(resource(_prot))
    tester = Sb.map_features_prot2dna(_prot, _dna)
    tester = Sb.order_ids(tester)
    assert seqs_to_hash(tester) == next_hash


# 'ri', '--rename_ids'
ri_hashes = ["0672973b580581f15cf2ce467b89144e", "3847ad5210a85b8db59e256261552ee7", "243024bfd2f686e6a6e0ef65aa963494",
             "83f10d1be7a5ba4d363eb406c1c84ac7", "973e3d7138b78db2bb3abda8a9323226", "4289f03afb6c9f8a8b0d8a75bb60a2ce"]
ri_hashes = [(Sb.SeqBuddy(resource(seq_files[indx])), value) for indx, value in enumerate(ri_hashes)]


@pytest.mark.parametrize("seqbuddy,next_hash", ri_hashes)
def test_rename_ids(seqbuddy, next_hash):  # Probably don't need to test ALL the files
    tester = Sb.rename(seqbuddy, 'Panx', 'Test', 0)
    assert seqs_to_hash(tester) == next_hash

# 'cf', '--combine_features'
cf_hashes = ["d6fbbf1cc2a654e1198a516cdd0f8889", "d6fbbf1cc2a654e1198a516cdd0f8889", "d6fbbf1cc2a654e1198a516cdd0f8889",
             "d6fbbf1cc2a654e1198a516cdd0f8889", "4d86c221a89b9e804a76c916d20e303a", "4d86c221a89b9e804a76c916d20e303a",
             "4d86c221a89b9e804a76c916d20e303a", "4d86c221a89b9e804a76c916d20e303a", "071475aa0566013628d420b89c4f602c",
             "071475aa0566013628d420b89c4f602c", "071475aa0566013628d420b89c4f602c", "071475aa0566013628d420b89c4f602c",
             "46ee4b02fbdfa31a5bd6e527e690d129", "46ee4b02fbdfa31a5bd6e527e690d129", "46ee4b02fbdfa31a5bd6e527e690d129",
             "46ee4b02fbdfa31a5bd6e527e690d129", "abc020b655549bad175d33077d1b307a", "abc020b655549bad175d33077d1b307a",
             "abc020b655549bad175d33077d1b307a", "abc020b655549bad175d33077d1b307a"]  # placeholders
cf_objects = []
hash_indx = 0
cf_list = seq_files[0:3]
cf_list.append(seq_files[4])
cf_list.append(seq_files[5])
for seq1 in cf_list:
    for seq2 in cf_list:
        if seq1 is not seq2:
            cf_objects.append((seq1, seq2, fd2p_hashes[hash_indx]))
            hash_indx += 1


@pytest.mark.parametrize("_seq1,_seq2,next_hash", cf_objects)
def test_combine_features(_seq1, _seq2, next_hash):
    _seq1 = Sb.SeqBuddy(resource(_seq1))
    _seq2 = Sb.SeqBuddy(resource(_seq2))
    tester = Sb.combine_features(_seq1, _seq2)
    assert seqs_to_hash(tester) == next_hash


# How do you test the 'shuffle' method?

# 'oi', '--order_ids'
oi_files = [seq_files[0], seq_files[6]]
oi_hashes = ["d103a7a41a5644614d59e0c44469d1b2", "945b2b43a423a5371ad7e90adda6e703"]
oi_hashes = [(Sb.SeqBuddy(resource(oi_files[indx])), value) for indx, value in enumerate(oi_hashes)]


@pytest.mark.parametrize("seqbuddy,next_hash", oi_hashes)
def test_order_ids(seqbuddy, next_hash):
    tester = Sb.order_ids(seqbuddy)
    assert seqs_to_hash(tester) == next_hash

oi_rev_hashes = ["3658c4b79cd7e8dfd6afe1a9cddc2dfa", "8c4e450b72410c37683f83e528c9a610"]
oi_rev_hashes = [(Sb.SeqBuddy(resource(oi_files[indx])), value) for indx, value in enumerate(oi_rev_hashes)]


@pytest.mark.parametrize("seqbuddy,next_hash", oi_rev_hashes)
def test_order_ids_rev(seqbuddy, next_hash):
    tester = Sb.order_ids(seqbuddy, _reverse=True)
    assert seqs_to_hash(tester) == next_hash

# 'ofp', '--order_features_by_position'
ofp_hashes = ["25073539df4a982b7f99c72dd280bb8f", "c10d136c93f41db280933d5b3468f187"]
ofp_hashes = [(Sb.SeqBuddy(resource(oi_files[indx])), value) for indx, value in enumerate(ofp_hashes)]


@pytest.mark.parametrize("seqbuddy, next_hash", ofp_hashes)
def test_order_features_by_position(seqbuddy, next_hash):
    tester = Sb.order_features_by_position(seqbuddy)
    assert seqs_to_hash(tester) == next_hash

ofp_rev_hashes = ["25073539df4a982b7f99c72dd280bb8f", "c10d136c93f41db280933d5b3468f187"]
ofp_rev_hashes = [(Sb.SeqBuddy(resource(oi_files[indx])), value) for indx, value in enumerate(ofp_rev_hashes)]


@pytest.mark.parametrize("seqbuddy, next_hash", ofp_rev_hashes)
def test_order_features_by_position_rev(seqbuddy, next_hash):
    tester = Sb.order_features_by_position(seqbuddy, _reverse=True)
    assert seqs_to_hash(tester) == next_hash

# 'sf', '--screw_formats'

# last three formats rebuilt each time to work correctly in parallel
fasta_files = ["Mnemiopsis/Mnemiopsis_cds.fa", "Mnemiopsis/Mnemiopsis_pep.fa"]
fasta_files = [Sb.SeqBuddy(resource(file)) for file in fasta_files]
gb_files = ["Mnemiopsis/Mnemiopsis_cds.gb", "Mnemiopsis/Mnemiopsis_pep.gb"]
gb_files = [Sb.SeqBuddy(resource(file)) for file in gb_files]
nex_files = ["Mnemiopsis/Mnemiopsis_cds.nex", "Mnemiopsis/Mnemiopsis_pep.nex"]
# nex_files = [Sb.SeqBuddy(resource(file)) for file in nex_files]
phyr_files = ["Mnemiopsis/Mnemiopsis_cds.phyr", "Mnemiopsis/Mnemiopsis_pep.phyr"]
# phyr_files = [Sb.SeqBuddy(resource(file)) for file in phyr_files]
stklm_files = ["Mnemiopsis/Mnemiopsis_cds.stklm", "Mnemiopsis/Mnemiopsis_pep.stklm"]
# stklm_files = [Sb.SeqBuddy(resource(file)) for file in stklm_files]


@pytest.mark.parametrize("_indx", [0, 1])
def test_screw_formats_fa_gb(_indx):
    fasta = fasta_files[_indx]
    gb = gb_files[_indx]
    assert seqs_to_hash(fasta) == seqs_to_hash(Sb.screw_formats(gb, "fasta"))

other_files = [nex_files, phyr_files, stklm_files]
screw_files = []
for l1 in other_files:
    for l2 in other_files:
        if l1 is not l2:
            for indx in range(3):
                screw_files.append((indx, l1, l2))


@pytest.mark.parametrize("indx,_l1,_l2", screw_files)  # fails when stklm is the out_format
def test_screw_formats_other(indx, _l1, _l2):
    sb1 = Sb.SeqBuddy(resource(_l1[indx]))
    sb2 = Sb.SeqBuddy(resource(_l2[indx]))
    sb2 = Sb.screw_formats(sb2, sb1.out_format)
    assert seqs_to_hash(sb1) == seqs_to_hash(sb2)

# 'er', '--extract_range'
er_hashes = ["1e31d4bc840532497e3e13f7f9ff2b6c", "0fd49e9218567966f4b00c44856662bc", "4063ab66ced2fafb080ceba88965d2bb",
             "0c857970ebef51b4bbd9c7b3229d7088", "e0e256cebd6ead99ed3a2a20b7417ba1", "d724df01ae688bfac4c6dfdc90027440",
             "e402f09afdb555bd8249d737dd7add99", "3b2f53ed43d9d0a771d6aad861a8ae34", "03cbca359b8674fdc6791590a329d807",
             "1d0ec72b618c165894c49d71de366302", "926e76bde33bfd5f4a588addfd7592b9", "6d6ac54cd809cf7d843beed8b362efb3"]
er_hashes = [(Sb.SeqBuddy(resource(seq_files[indx])), value) for indx, value in enumerate(er_hashes)]


@pytest.mark.parametrize("seqbuddy,next_hash", er_hashes)
def test_extract_range(seqbuddy, next_hash):
    tester = Sb.extract_range(seqbuddy, 50, 300)
    assert seqs_to_hash(tester) == next_hash


def test_extract_range_end_less_than_start():
    seqbuddy = Sb.SeqBuddy(resource("Mnemiopsis/Mnemiopsis_cds.fa"))
    with pytest.raises(AttributeError):
        Sb.extract_range(seqbuddy, 500, 50)

# 'ns', '--num_seqs'
ns_files = [(Sb.SeqBuddy(resource("ns/20.fa")), 20), (Sb.SeqBuddy(resource("ns/5.fa")), 5),
            (Sb.SeqBuddy(resource("ns/1.fa")), 1)]


@pytest.mark.parametrize("seqbuddy, num", ns_files)
def test_num_seqs(seqbuddy, num):
    assert Sb.num_seqs(seqbuddy) == num


def test_empty_file():
    with pytest.raises(SystemExit):
        Sb.SeqBuddy(resource("ns/blank.fa"))

if __name__ == '__main__':
    debug = Sb.order_features_alphabetically(sb_objects[1])
    print(seqs_to_hash(debug, "string"))
"""