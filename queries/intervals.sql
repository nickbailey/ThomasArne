select populateDocument('inv', score_notes) from score_notes where work_id = :workID ;

begin;
  create temp table bi as (
    select top.work_id,
           top.note_id,
           top.voice,
           top.part_id,
           getinterval(top.pitch, bottom.pitch) as value
        from score_notes as top
               inner join score_notes as bottom
               on (
                 bottom.work_id = top.work_id
                   and bottom.part_id = 'XPart 0'
                   and bottom.type = 'pitch'
                   and (
                     bottom.onset = top.onset
                     or (bottom.onset < top.onset and bottom.onset + bottom.duration > top.onset)
                   )
               )
    where top.part_id = 'XPart 1'
          and top.type = 'pitch'
          and top.work_id = :workID
    order by top.onset, bottom.onset
  )
  ;

  select addtextundernotes('inv',
                           'intervs',
                           cast (
                                  ( bi.work_id,
                                    bi.note_id,
                                    bi.voice,
                                    bi.part_id,
                                    E' \\with-color #red ' || interval2text(bi.value)
                                  ) as spoff_text_type
                                )
                           )
      from bi
  where equateIntervalClass(bi.value, text2interval('M2'))
        or equateIntervalClass(bi.value, text2interval('P4'))
        or equateIntervalClass(bi.value, text2interval('M7'))
  ;

  select addtextundernotes('inv',
                           'intervs',
                           cast(
                                 ( bi.work_id,
                                   bi.note_id,
                                   bi.voice,
                                   bi.part_id,
                                   interval2text(bi.value)
                                 ) as spoff_text_type
                               )
                          )
      from bi
  where not equateIntervalClass(bi.value, text2interval('M2'))
        and not equateIntervalClass(bi.value, text2interval('P4'))
        and not equateIntervalClass(bi.value, text2interval('M7'))
  ;

  drop table bi;
commit;

begin;
  create temp table bi as (
    select bottom.work_id,
           bottom.note_id,
           bottom.voice,
           bottom.part_id,
           getinterval(top.pitch, bottom.pitch) as value
         from score_notes as top
                inner join score_notes as bottom
                on (
                  bottom.work_id = top.work_id
                    and bottom.part_id = 'XPart 0'
                    and bottom.type = 'pitch'
                    and (
                      bottom.onset >= top.onset 
                        and bottom.onset < top.onset + top.duration
                    )
                )
    where top.part_id = 'XPart 1'
          and top.type = 'pitch'
          and top.work_id = :workID
    order by top.onset, bottom.onset
  );

  select addtextundernotes('inv',
                           'intervs',
                           cast (
                                  ( bi.work_id,
                                    bi.note_id,
                                    bi.voice,
                                    bi.part_id,
                                    E' \\with-color #red ' || interval2text(bi.value)
                                   ) as spoff_text_type
                                )
                           )
      from bi
    where equateIntervalClass(bi.value, text2interval('M2'))
          or equateIntervalClass(bi.value, text2interval('P4'))
          or equateIntervalClass(bi.value, text2interval('M7'))
  ;

  select addtextundernotes('inv',
                           'intervs',
                           cast (
                                  ( bi.work_id,
                                    bi.note_id,
                                    bi.voice,
                                    bi.part_id,
                                    interval2text(bi.value)
                                  ) as spoff_text_type
                                )
                          )
      from bi
    where not equateIntervalClass(bi.value, text2interval('M2'))
          and not equateIntervalClass(bi.value, text2interval('P4'))
          and not equateIntervalClass(bi.value, text2interval('M7'))
  ;

  drop table bi;
commit;

