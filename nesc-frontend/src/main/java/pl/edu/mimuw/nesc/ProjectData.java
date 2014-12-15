package pl.edu.mimuw.nesc;

import com.google.common.base.Optional;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import pl.edu.mimuw.nesc.names.mangling.NameMangler;
import pl.edu.mimuw.nesc.problem.NescIssue;

import java.util.Collection;

/**
 * Contains the result of parsing process for entire project.
 *
 * @author Grzegorz Kołakowski <gk291583@students.mimuw.edu.pl>
 */
public final class ProjectData {

    public static Builder builder() {
        return new Builder();
    }

    private final ImmutableMap<String, FileData> fileDatas;
    private final ImmutableMap<String, String> globalNames;
    private final Optional<FileData> rootFileData;
    private final ImmutableList<NescIssue> issues;
    private final NameMangler nameMangler;

    private ProjectData(Builder builder) {
        builder.buildMaps();

        this.fileDatas = builder.fileDatas;
        this.globalNames = builder.globalNames;
        this.rootFileData = Optional.fromNullable(builder.rootFileData);
        this.issues = builder.issueListBuilder.build();
        this.nameMangler = builder.nameMangler;
    }

    public ImmutableMap<String, FileData> getFileDatas() {
        return fileDatas;
    }

    /**
     * Map with unique names of entities that are to be located in the global
     * scope mapped to their normal names as they appear in the code. The names
     * are for the entire project.
     *
     * @return Mapping of unique names of global entities to their normal names.
     */
    public ImmutableMap<String, String> getGlobalNames() {
        return globalNames;
    }

    public Optional<FileData> getRootFileData() {
        return rootFileData;
    }

    public ImmutableList<NescIssue> getIssues() {
        return issues;
    }

    /**
     * <p>Get name mangler that has been used to mangle names in the NesC
     * application and can be used to generate new unique names for it.
     * If the frontend instance used to create this project data processes
     * files, then the state of the mangler can change.</p>
     *
     * <p>If this project contains some errors, then the returned value may be
     * <code>null</code>.</p>
     *
     * @return Name mangler for further unique names generation.
     */
    public NameMangler getNameMangler() {
        return nameMangler;
    }

    /**
     * @author Grzegorz Kołakowski <gk291583@students.mimuw.edu.pl>
     */
    public static class Builder {

        private ImmutableMap.Builder<String, FileData> fileDataBuilder;
        private ImmutableList.Builder<NescIssue> issueListBuilder;
        private FileData rootFileData;

        private ImmutableMap<String, FileData> fileDatas;
        private ImmutableMap<String, String> globalNames;

        private NameMangler nameMangler;

        public Builder() {
            this.fileDataBuilder = ImmutableMap.builder();
            this.issueListBuilder = ImmutableList.builder();
        }

        public Builder addRootFileData(FileData fileData) {
            this.rootFileData = fileData;
            return this;
        }

        public Builder addFileDatas(Collection<FileData> fileDatas) {
            for (FileData data : fileDatas) {
                this.fileDataBuilder.put(data.getFilePath(), data);
            }
            return this;
        }

        public Builder addIssue(NescIssue issue) {
            this.issueListBuilder.add(issue);
            return this;
        }

        public Builder addIssues(Collection<NescIssue> issues) {
            this.issueListBuilder.addAll(issues);
            return this;
        }

        public Builder nameMangler(NameMangler nameMangler) {
            this.nameMangler = nameMangler;
            return this;
        }

        public ProjectData build() {
            verify();
            return new ProjectData(this);
        }

        private void verify() {
        }

        private void buildMaps() {
            this.fileDatas = fileDataBuilder.build();

            final ImmutableMap.Builder<String, String> globalNamesBuilder = ImmutableMap.builder();
            for (FileData fileData : this.fileDatas.values()) {
                globalNamesBuilder.putAll(fileData.getGlobalNames());
            }

            this.globalNames = globalNamesBuilder.build();
        }
    }
}
